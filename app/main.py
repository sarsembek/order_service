import bcrypt
from fastapi.responses import JSONResponse
from fastapi import status

from app.core.exceptions.custom_exceptions import AuthException, InsufficientStockError, OrderNotFoundError, ProductNotFoundError, UnauthorizedOrderAccessError
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("dummy", (), {"__version__": "4.2.1"})

from fastapi import FastAPI, Request
from app.routers.api import api_router

app = FastAPI()
app.include_router(api_router)

@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": str(exc),
            "error_type": exc.__class__.__name__,
            **exc.__dict__
        }
    )

# Product-related exceptions
@app.exception_handler(ProductNotFoundError)
async def product_not_found_handler(request: Request, exc: ProductNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": str(exc),
            "product_id": exc.product_id,
            "error_type": "ProductNotFoundError"
        }
    )

@app.exception_handler(InsufficientStockError)
async def insufficient_stock_handler(request: Request, exc: InsufficientStockError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": str(exc),
            "product_id": exc.product_id,
            "available": exc.available,
            "error_type": "InsufficientStockError"
        }
    )

# Order-related exceptions
@app.exception_handler(UnauthorizedOrderAccessError)
async def unauthorized_order_handler(request: Request, exc: UnauthorizedOrderAccessError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "detail": str(exc),
            "order_id": exc.order_id,
            "error_type": "UnauthorizedOrderAccessError"
        }
    )

@app.exception_handler(OrderNotFoundError)
async def order_not_found_handler(request: Request, exc: OrderNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": str(exc),
            "order_id": exc.order_id,
            "error_type": "OrderNotFoundError"
        }
    )
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
