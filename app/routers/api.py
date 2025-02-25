from fastapi import APIRouter
from app.routers.auth import router as auth_router
from app.routers.orders import router as orders_router
from app.routers.exception_handlers import router as exception_router

api_router = APIRouter()
api_router.include_router(exception_router)
api_router.include_router(auth_router)
api_router.include_router(orders_router)