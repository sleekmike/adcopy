"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App Settings
    APP_NAME: str = "AI Ad Copy Generator"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "ad_copy_generator"
    
    # DeepSeek API
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # Rate Limiting (for MVP)
    MAX_REQUESTS_PER_MINUTE: int = 60
    MAX_ADS_PER_REQUEST: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
