"""
Application Configuration

Simple settings management using pydantic-settings.
Add your own settings as needed.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings from environment variables.
    
    Configure via .env file or environment variables.
    """
    
    # Basic settings
    PROJECT_NAME: str = "{{project_name}}"
    PROJECT_DESCRIPTION: str = "A FastAPI project"
    VERSION: str = "0.1.0"
    
    # Environment
    DEBUG: bool = True
    
    # Add your settings here
    # DATABASE_URL: str = "sqlite:///./app.db"
    # SECRET_KEY: str = "your-secret-key"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
