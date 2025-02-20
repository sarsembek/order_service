from typing import List
from sqlalchemy.orm import Session
from app.core.models.product import Product
from app.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self, repository: ProductRepository, db: Session) -> None:
        self.repository = repository
        self.db = db

    def create_product(self, name: str, price: int, quantity: int) -> Product:
        product = Product(name=name, price=price, quantity=quantity)
        return self.repository.create(product)

    def get_product(self, product_id: int) -> Product:
        product = self.repository.get(product_id)
        if not product:
            raise Exception("Product not found")
        return product

    def list_products(self) -> List[Product]:
        return self.repository.list_all()