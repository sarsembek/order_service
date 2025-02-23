from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Integer)
    quantity = Column(Integer)
    
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        secondary="order_product_association",
        back_populates="products"
    )