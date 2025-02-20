from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.models.order import Order, OrderStatus
from app.core.schemas.order_schema import OrderCreateSchema
from app.repositories.order_repository import OrderRepository
from app.core.models.user import User

class OrderService:
    def __init__(self, repository: OrderRepository, db: Session) -> None:
        self.repository = repository
        self.db = db

    def create_order(self, order_data: OrderCreateSchema, current_user: User) -> Order:
        new_order = Order(
            customer_name=current_user.username,
            order_status=order_data.status,
            total_price=int(order_data.total_price)
            # Note: Product handling omitted for simplicity.
        )
        return self.repository.create(new_order)

    def update_order(self, order_id: int, order_data: OrderCreateSchema, current_user: User) -> Order:
        order = self.repository.get(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

        if not current_user.is_admin and order.customer_name != current_user.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this order"
            )
        update_data = order_data.dict()
        return self.repository.update(order, update_data)

    def get_orders(
        self, 
        current_user: User, 
        status_filter: Optional[OrderStatus] = None, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None
    ) -> List[Order]:
        orders = self.repository.list_all()

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
        order = self.repository.get(order_id)
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
        return self.repository.update(order, {"order_status": OrderStatus.CANCELLED})