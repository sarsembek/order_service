from sqlalchemy.orm import Session
from app.core.models.order import Order

class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, order: Order) -> Order:
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    def get(self, order_id: int) -> Order:
        return self.session.query(Order).filter(Order.order_id == order_id).first()

    def list_all(self) -> list[Order]:
        return self.session.query(Order).all()

    def update(self, order: Order, data: dict) -> Order:
        for key, value in data.items():
            setattr(order, key, value)
        self.session.commit()
        self.session.refresh(order)
        return order

    def delete(self, order: Order) -> None:
        self.session.delete(order)
        self.session.commit()