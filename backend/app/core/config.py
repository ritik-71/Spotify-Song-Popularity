# backend/app/core/config.py
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    PROJECT_NAME: str = "MuseMind AI: Enterprise Music Intelligence Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security Configurations
    JWT_SECRET: str = "SUPER_SECURE_MUSEMIND_JWT_SECRET_KEY_FOR_LOCAL_DEV_2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Database Configurations
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "musemind"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Cache Configurations
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # MLOps and Vector Database URLs
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    QDRANT_URL: str = "http://localhost:6333"
    
    # LLM Settings
    GEMINI_API_KEY: str = "MOCK_GEMINI_KEY"
    
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_file_encoding="utf-8")

settings = Settings()
