from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class OrderProductAssociation(Base):
    __tablename__ = "order_product_association"

    order_id = Column(Integer, ForeignKey("orders.order_id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)

    ordered_quantity = Column(Integer, nullable=False)

    product = relationship("Product", back_populates="order_associations")
    order = relationship("Order", back_populates="order_associations")
    
    @property
    def quantity(self) -> int:
        return self.ordered_quantity