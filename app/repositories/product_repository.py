from sqlalchemy.orm import Session
from app.core.models.product import Product

class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, product: Product) -> Product:
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def get(self, product_id: int) -> Product:
        return self.session.query(Product).filter(Product.product_id == product_id).first()

    def list_all(self) -> list[Product]:
        return self.session.query(Product).all()

    def update(self, product: Product, data: dict) -> Product:
        for key, value in data.items():
            setattr(product, key, value)
        self.session.commit()
        self.session.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.session.delete(product)
        self.session.commit()