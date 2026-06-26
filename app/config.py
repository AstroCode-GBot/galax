import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_ID: int
    SECRET_KEY: str
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    ENVIRONMENT: str = "production"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()