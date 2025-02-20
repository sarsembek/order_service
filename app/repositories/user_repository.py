from sqlalchemy.orm import Session
from app.core.models.user import User

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get(self, user_id: int) -> User:
        return self.session.query(User).filter(User.user_id == user_id).first()

    def get_by_username(self, username: str) -> User:
        return self.session.query(User).filter(User.username == username).first()

    def list_all(self) -> list[User]:
        return self.session.query(User).all()

    def update(self, user: User, data: dict) -> User:
        for key, value in data.items():
            setattr(user, key, value)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.commit()