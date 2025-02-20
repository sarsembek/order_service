from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.dependencies import get_db
from app.services.auth_service import AuthService
from app.core.schemas.user_schema import UserCreateSchema, LoginSchema, Token, UserSchema

router = APIRouter(prefix="/auth", tags=["auth"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post("/register", response_model=UserSchema)
def register(user_data: UserCreateSchema, service: AuthService = Depends(get_auth_service)):
    return service.register(user_data)

@router.post("/login", response_model=Token)
def login(login_data: LoginSchema, service: AuthService = Depends(get_auth_service)):
    return service.login(login_data)

class RefreshSchema(BaseModel):
    token: str

@router.post("/refresh", response_model=Token)
def refresh(refresh_data: RefreshSchema, service: AuthService = Depends(get_auth_service)):
    return service.refresh(refresh_data.token)