from pydantic import BaseModel


class ProductSchema(BaseModel):
    product_id: int
    name: str
    price: int
    quantity: int

    class Config:
        from_attributes = True
        
class ProductCreateSchema(BaseModel):
    name: str
    price: float
    quantity: int