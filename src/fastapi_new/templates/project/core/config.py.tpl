"""
Application Configuration
Manages all settings through environment variables and .env files.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Usage:
        from app.core.config import settings
        print(settings.PROJECT_NAME)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Project Info
    PROJECT_NAME: str = "{{project_name}}"
    PROJECT_DESCRIPTION: str = "A FastAPI project built with FastAPI-New"
    VERSION: str = "0.1.0"

    # Environment
    ENVIRONMENT: Literal["dev", "staging", "prod"] = "dev"
    DEBUG: bool = True

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    OPENAPI_URL: bool = True
    DOCS_URL: bool = True
    REDOC_URL: bool = True

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    WORKERS: int = 1

    # Database Settings
    DATABASE_ENGINE: Literal["postgres", "mysql", "sqlite", "mongodb"] = "sqlite"
    DATABASE_URL: str = "sqlite:///./app.db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Security Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # CORS Settings
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    @property
    def is_dev(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "dev"

    @property
    def is_prod(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "prod"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures settings are only loaded once.
    """
    return Settings()


# Global settings instance
settings = get_settings()
