from typing import List
from pydantic import BaseModel
from app.core.models.order import OrderStatus

class OrderProductSchema(BaseModel):
    product_id: int
    quantity: int 

    model_config = {
        "from_attributes": True
    }

class OrderSchema(BaseModel):
    order_id: int
    customer_name: str
    order_status: OrderStatus
    total_price: int
    products: List[OrderProductSchema]

    model_config = {
        "from_attributes": True
    }

class OrderCreateSchema(BaseModel):
    products: List[OrderProductSchema]