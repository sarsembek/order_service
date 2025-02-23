from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database import Base

order_product_association = Table(
    "order_product_association",
    Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.order_id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.product_id"), primary_key=True),
)