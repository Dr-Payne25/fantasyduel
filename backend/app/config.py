from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "sqlite:///./fantasyduel.db"
    sleeper_api_base: str = "https://api.sleeper.app/v1"
    secret_key: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()