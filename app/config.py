from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "RECRUITING2.0"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()