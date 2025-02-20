from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from pydantic import BaseModel

from app.dependencies import get_db
from app.services.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.repositories.user_repository import UserRepository
from app.core.models.user import User
from app.core.schemas.user_schema import LoginSchema, Token, UserCreateSchema, UserSchema

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserSchema)
def register(user_data: UserCreateSchema, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    if user_repo.get_by_username(user_data.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    created_user = user_repo.create(new_user)
    return created_user

@router.post("/login", response_model=Token)
def login(login_data: LoginSchema, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(login_data.username)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.user_id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

class RefreshSchema(BaseModel):
    token: str

@router.post("/refresh", response_model=Token)
def refresh(refresh_data: RefreshSchema):
    token = refresh_data.token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_token = create_access_token(
        data={"sub": username},
        expires_delta=access_token_expires
    )
    return {"access_token": new_token, "token_type": "bearer"}