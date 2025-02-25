from fastapi import APIRouter
from app.routers.auth import router as auth_router
from app.routers.orders import router as orders_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(orders_router)