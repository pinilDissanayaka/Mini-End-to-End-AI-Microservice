import os
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Centralized configuration settings for the application"""
    
    # Application Settings
    APP_NAME: str
    APP_VERSION: str
    APP_DESCRIPTION: str
    DEBUG: bool = False
    HOST: str
    PORT: int
    
    # Database Settings
    DATABASE_URL: str
    DATABASE_ECHO: bool = True
    
    # Redis Settings
    REDIS_URL: str
    
    # LLM Model Settings
    CHAT_MODEL: str
    LLM_TEMPERATURE: float
    LLM_MAX_NEW_TOKENS: int
    LLM_REPETITION_PENALTY: float
    
    # Embedding Model Settings
    EMBEDDING_MODEL: str
    EMBEDDING_DEVICE: str
    EMBEDDING_NORMALIZE: bool
    
    # Vector Store Settings
    VECTOR_STORE_PATH: str
    VECTOR_STORE_COLLECTION: str
    
    # File Upload Settings
    UPLOAD_DIR: str
    MAX_UPLOAD_SIZE: int
    ALLOWED_EXTENSIONS: set = {".pdf", ".txt", ".json", ".md", ".docx", ".pptx"}
    
    # CORS Settings
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # Logging Settings
    LOG_LEVEL: str
    LOG_FORMAT: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure upload directory exists
        Path(self.UPLOAD_DIR).mkdir(exist_ok=True)


# Global settings instance
config = Settings()
