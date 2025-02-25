from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    DB_URL: str = "sqlite:///./test.db"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    DB_USER: str = "order_user"
    DB_PASSWORD: str = "order_service2025"
    DB_NAME: str = "order_service"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

settings = Settings()
