from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    DATABASE_URL: str
    AUDIT_DATABASE_URL: str
    SECRET_KEY: str
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    GEMINI_MODEL: str = "gemini-1.5-flash"
    RATE_LIMIT_PER_MINUTE: int = 10
    QUERY_TIMEOUT_SECONDS: int = 5
    # PostgreSQL role credentials (used for role creation)
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    AUDIT_USER: str
    AUDIT_PASSWORD: str

    # Resolve .env relative to the project root (two levels up from this file)
    PROJECT_ROOT: ClassVar[Path] = Path(__file__).resolve().parents[2]
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", case_sensitive=True)

@lru_cache()
def get_settings() -> Settings:
    return Settings()
