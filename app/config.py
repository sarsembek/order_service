from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    class Config:
        env_file = ".env" 

settings = Settings()