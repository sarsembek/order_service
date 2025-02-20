import enum
from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    order_status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_price = Column(Integer)
    products = relationship("Product", secondary="order_products", back_populates="orders")