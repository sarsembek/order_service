from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.core.schemas.order_schema import OrderCreateSchema, OrderSchema
from app.core.models.order import OrderStatus
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService
from app.core.models.user import User

router = APIRouter(prefix="/orders", tags=["orders"])


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    repository = OrderRepository(db)
    return OrderService(repository=repository, db=db)


@router.post("", response_model=OrderSchema)
def create_order(
    order_data: OrderCreateSchema, 
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    return service.create_order(order_data, current_user)


@router.put("/{order_id}", response_model=OrderSchema)
def update_order(
    order_id: int, 
    order_data: OrderCreateSchema, 
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    return service.update_order(order_id, order_data, current_user)


@router.get("", response_model=List[OrderSchema])
def list_orders(
    status: Optional[OrderStatus] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    return service.get_orders(current_user, status_filter=status, min_price=min_price, max_price=max_price)


@router.get("/{order_id}", response_model=OrderSchema)
def get_order(
    order_id: int, 
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    return service.get_order(order_id, current_user)


@router.delete("/{order_id}", response_model=OrderSchema)
def soft_delete_order(
    order_id: int, 
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    return service.soft_delete_order(order_id, current_user)