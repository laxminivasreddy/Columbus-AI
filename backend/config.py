from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    anthropic_api_key: str
    gemini_api_key: str = ""
    mongodb_url: str = "mongodb://localhost:27017"
    redis_url: str = "redis://localhost:6379"
    weather_api_key: str = ""
    rapidapi_key: str = ""
    chroma_persist_dir: str = "../chroma_db"
    faiss_index_path: str = "../faiss_index"
    secret_key: str = "change-me"
    debug: bool = False

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()
