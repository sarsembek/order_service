from datetime import timedelta
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.core.models.user import User
from app.core.schemas.user_schema import UserCreateSchema, LoginSchema
from app.utils.auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.core.exceptions.custom_exceptions import DuplicateUsernameError, InvalidCredentialsError, TokenExpiredError, TokenInvalidError

class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, user_data: UserCreateSchema) -> User:
        if self.user_repo.get_by_username(user_data.username):
            raise DuplicateUsernameError("Username already registered")
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        return self.user_repo.create(new_user)

    def login(self, login_data: LoginSchema) -> dict:
        user = self.user_repo.get_by_username(login_data.username)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise InvalidCredentialsError("Incorrect username or password")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.user_id},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    def refresh(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if not username:
                raise TokenInvalidError()
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except JWTError as e:
            raise TokenInvalidError(str(e))
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_token = create_access_token(
            data={"sub": username},
            expires_delta=access_token_expires
        )
        return {"access_token": new_token, "token_type": "bearer"}