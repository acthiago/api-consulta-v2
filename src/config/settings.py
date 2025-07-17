"""
Configurações centralizadas da aplicação usando Pydantic Settings
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configurações da aplicação usando Pydantic Settings"""
    
    # Application
    APP_NAME: str = Field("API de Consulta e Cobranças v2", env="APP_NAME")
    APP_VERSION: str = Field("2.0.0", env="APP_VERSION") 
    APP_DESCRIPTION: str = Field("API com Arquitetura Hexagonal", env="APP_DESCRIPTION")
    DEBUG: bool = Field(False, env="DEBUG")
    ENVIRONMENT: str = Field("production", env="ENVIRONMENT")
    
    # Server
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")
    RELOAD: bool = Field(False, env="RELOAD")
    
    # Security
    SECRET_KEY: str = Field("change-this-secret-key", env="SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Database
    MONGO_URI: str = Field("mongodb://localhost:27017", env="MONGO_URI")
    MONGO_DB_NAME: str = Field("api_consulta_v2", env="MONGO_DB_NAME")
    MONGO_MIN_POOL_SIZE: int = Field(10, env="MONGO_MIN_POOL_SIZE")
    MONGO_MAX_POOL_SIZE: int = Field(100, env="MONGO_MAX_POOL_SIZE")
    MONGO_MAX_IDLE_TIME_MS: int = Field(30000, env="MONGO_MAX_IDLE_TIME_MS")
    
    # Cache
    REDIS_URL: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    CACHE_TTL_SECONDS: int = Field(300, env="CACHE_TTL_SECONDS")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(1000, env="RATE_LIMIT_PER_HOUR")
    RATE_LIMIT_PER_DAY: int = Field(10000, env="RATE_LIMIT_PER_DAY")
    
    # CORS
    ENABLE_CORS: bool = Field(True, env="ENABLE_CORS")
    CORS_ORIGINS: List[str] = Field(["http://localhost:3000"], env="CORS_ORIGINS")
    
    # Documentation
    ENABLE_DOCS: bool = Field(True, env="ENABLE_DOCS")
    DOCS_URL: str = Field("/docs", env="DOCS_URL")
    REDOC_URL: str = Field("/redoc", env="REDOC_URL")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(True, env="ENABLE_METRICS")
    METRICS_PATH: str = Field("/metrics", env="METRICS_PATH")
    
    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field("json", env="LOG_FORMAT")
    LOG_FILE: Optional[str] = Field(None, env="LOG_FILE")
    
    # Storage
    STORAGE_TYPE: str = Field("local", env="STORAGE_TYPE")
    STORAGE_PATH: str = Field("./storage", env="STORAGE_PATH")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings