import enum
from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship, Mapped
from app.database import Base
from app.core.models.order_association import OrderProductAssociation

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
    
    order_associations: Mapped[list[OrderProductAssociation]] = relationship(
        "OrderProductAssociation",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    
    @property
    def products(self):
        return [assoc.product for assoc in self.order_associations]
    
    @property
    def status(self):
        return self.order_status