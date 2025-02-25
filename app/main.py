import bcrypt
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("dummy", (), {"__version__": "4.2.1"})

from fastapi import FastAPI
from app.routers.api import api_router

app = FastAPI()
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
