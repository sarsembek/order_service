from typing import List
from pydantic import BaseModel

from app.core.models.order import OrderStatus
from app.core.schemas.product_schema import ProductCreateSchema, ProductSchema

class OrderSchema(BaseModel):
    order_id: int
    customer_name: str
    status: OrderStatus
    total_price: int
    products: List[ProductSchema]

    class Config:
        from_attributes = True
        
class OrderCreateSchema(BaseModel):
    customer_name: str
    status: OrderStatus = OrderStatus.PENDING
    total_price: float
    products: List[ProductCreateSchema]