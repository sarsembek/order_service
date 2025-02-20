import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    # For SQLite, you might use:
    DB_URL: str = os.getenv("DB_URL", "sqlite:///./test.db")

settings = Settings()