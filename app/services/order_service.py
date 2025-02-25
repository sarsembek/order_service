import json
import redis
from typing import List, Optional, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.models.order import Order, OrderStatus
from app.core.schemas.order_schema import OrderCreateSchema, OrderSchema
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.core.models.user import User
from app.core.models.order_association import OrderProductAssociation

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

    def create_order(self, order_data: OrderCreateSchema, current_user: User) -> Order:
        total_price = 0
        product_repo = ProductRepository(self.db)
        # Set order_status to pending; ignore incoming status field if any.
        new_order = Order(
            customer_name=current_user.username,  # Always taken from token
            order_status=OrderStatus.PENDING,
            total_price=0  # Will be updated below
        )

        for prod_data in order_data.products:
            product = product_repo.get(prod_data.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with ID '{prod_data.product_id}' not found"
                )
            if product.quantity < prod_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough quantity for product with ID '{prod_data.product_id}'. Available: {product.quantity}"
                )

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
        return created_order

    def update_order(self, order_id: int, order_data: OrderCreateSchema, current_user: User) -> Order:
        order = self.repository.get(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )
        if not current_user.is_admin and order.customer_name != current_user.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this order"
            )
        update_data = order_data.dict()
        updated_order = self.repository.update(order, update_data)

        self.cache[updated_order.order_id] = updated_order
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
        # Try to retrieve from Redis cache
        cached = self._get_cached_order(order_id)
        if cached:
            # Optionally, you can use OrderSchema.parse_obj to validate the structure
            # and then convert it to your ORM model if needed.
            # Here we just return the cached dict and assume FastAPI converts it appropriately.
            # If you prefer to return an ORM instance, fetch from the DB.
            return cached
        
        order = self.repository.get(order_id)
        if order:
            self.cache[order.order_id] = order
            self._cache_order(order)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )
        if not current_user.is_admin and order.customer_name != current_user.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this order"
            )
        return order

    def soft_delete_order(self, order_id: int, current_user: User) -> Order:
        order = self.repository.get(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )
        if not current_user.is_admin and order.customer_name != current_user.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this order"
            )
        updated_order = self.repository.update(order, {"order_status": OrderStatus.CANCELLED})

        self.cache[order_id] = updated_order
        return updated_order