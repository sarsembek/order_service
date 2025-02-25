import json
import redis
import logging
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from app.config import settings
from app.core.models.order import Order, OrderStatus
from app.core.schemas.order_schema import OrderCreateSchema, OrderSchema
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.core.models.user import User
from app.core.models.order_association import OrderProductAssociation
from app.core.exceptions import (
    ProductNotFoundError,
    InsufficientStockError,
    UnauthorizedOrderAccessError,
    OrderNotFoundError
)

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, repository: OrderRepository, db: Session) -> None:
        self.repository = repository
        self.db = db
        # In-memory cache fallback (if needed)
        self.cache: Dict[int, Order] = {}
        # Redis client for caching orders
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

    def _cache_order(self, order: Order) -> None:
        key = f"order:{order.order_id}"
        order_data = OrderSchema.from_orm(order).dict()
        self.redis.set(key, json.dumps(order_data))
        
    def _get_cached_order(self, order_id: int) -> Optional[dict]:
        key = f"order:{order_id}"
        cached = self.redis.get(key)
        return json.loads(cached) if cached else None

    def _log_status_change(self, order_id: int, old_status: OrderStatus, new_status: OrderStatus) -> None:
        logger.info(f"Order status changed: order_id={order_id}, old_status={old_status}, new_status={new_status}")

    def create_order(self, order_data: OrderCreateSchema, current_user: User) -> Order:
        total_price = 0
        product_repo = ProductRepository(self.db)
        new_order = Order(
            customer_name=current_user.username,  # always taken from token
            order_status=OrderStatus.PENDING,
            total_price=0  # will be updated below
        )

        for prod_data in order_data.products:
            product = product_repo.get(prod_data.product_id)
            if not product:
                raise ProductNotFoundError(prod_data.product_id)
            if product.quantity < prod_data.quantity:
                raise InsufficientStockError(prod_data.product_id, product.quantity)

            product.quantity -= prod_data.quantity
            subtotal = product.price * prod_data.quantity
            total_price += subtotal

            association = OrderProductAssociation(
                product_id=product.product_id,
                ordered_quantity=prod_data.quantity
            )
            new_order.order_associations.append(association)
        new_order.total_price = total_price
        created_order = self.repository.create(new_order)
        self.cache[created_order.order_id] = created_order
        self._cache_order(created_order)
        
        # Log the creation action
        logger.info(f"Order created: {created_order.order_id} by user: {current_user.username}")
        
        return created_order

    def update_order(self, order_id: int, order_data: OrderCreateSchema, current_user: User) -> Order:
        order = self.repository.get(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        if not current_user.is_admin and order.customer_name != current_user.username:
            raise UnauthorizedOrderAccessError(order_id)
        
        old_status = order.order_status
        update_data = order_data.dict()
        updated_order = self.repository.update(order, update_data)
        self.cache[updated_order.order_id] = updated_order
        self._cache_order(updated_order)
        
        # Log the update action
        logger.info(f"Order updated: {updated_order.order_id} by user: {current_user.username}")
        
        # Log the status change if it occurred
        if old_status != updated_order.order_status:
            self._log_status_change(updated_order.order_id, old_status, updated_order.order_status)
        
        return updated_order

    def get_orders(
        self, 
        current_user: User, 
        status_filter: Optional[OrderStatus] = None, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None
    ) -> List[Order]:
        orders = self.repository.list_all()

        for order in orders:
            self.cache[order.order_id] = order
        if not current_user.is_admin:
            orders = [o for o in orders if o.customer_name == current_user.username]
        if status_filter:
            orders = [o for o in orders if o.order_status == status_filter]
        if min_price is not None:
            orders = [o for o in orders if o.total_price is not None and o.total_price >= min_price]
        if max_price is not None:
            orders = [o for o in orders if o.total_price is not None and o.total_price <= max_price]
        return orders

    def get_order(self, order_id: int, current_user: User) -> Order:
        cached = self._get_cached_order(order_id)
        if cached:
            return cached
        
        order = self.repository.get(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        if not current_user.is_admin and order.customer_name != current_user.username:
            raise UnauthorizedOrderAccessError(order_id)
        self.cache[order.order_id] = order
        self._cache_order(order)
        return order

    def soft_delete_order(self, order_id: int, current_user: User) -> Order:
        order = self.repository.get(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        if not current_user.is_admin and order.customer_name != current_user.username:
            raise UnauthorizedOrderAccessError(order_id)
        
        old_status = order.order_status
        updated_order = self.repository.update(order, {"order_status": OrderStatus.CANCELLED})
        self.cache[order_id] = updated_order
        self._cache_order(updated_order)
        
        # Log the deletion action
        logger.info(f"Order soft-deleted: {updated_order.order_id} by user: {current_user.username}")
        
        # Log the status change
        self._log_status_change(updated_order.order_id, old_status, updated_order.order_status)
        
        return updated_order