from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped
from app.database import Base
from app.core.models.order_association import OrderProductAssociation

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Integer)
    quantity = Column(Integer)  # available stock
    
    order_associations: Mapped[list[OrderProductAssociation]] = relationship(
        "OrderProductAssociation",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    
    @property
    def orders(self):
        return [assoc.order for assoc in self.order_associations]