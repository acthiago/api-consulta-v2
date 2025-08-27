"""
Configurações centralizadas da aplicação usando Pydantic Settings
"""

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação usando Pydantic Settings"""

    # Application
    APP_NAME: str = Field(default="API de Consulta e Cobranças v2")
    APP_VERSION: str = Field(default="2.1.0")
    APP_DESCRIPTION: str = Field(default="Sistema Completo de Gestão Financeira")
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="production")

    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    RELOAD: bool = Field(default=False)

    # Security
    SECRET_KEY: str = Field(default="change-this-secret-key")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Database
    MONGO_URI: str = Field(default="mongodb://localhost:27017")
    MONGO_DB_NAME: str = Field(default="api_consulta_v2")
    MONGO_MIN_POOL_SIZE: int = Field(default=10)
    MONGO_MAX_POOL_SIZE: int = Field(default=100)
    MONGO_MAX_IDLE_TIME_MS: int = Field(default=30000)

    # Cache
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CACHE_TTL_SECONDS: int = Field(default=300)

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)
    RATE_LIMIT_PER_HOUR: int = Field(default=1000)
    RATE_LIMIT_PER_DAY: int = Field(default=10000)

    # CORS
    ENABLE_CORS: bool = Field(default=True)
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"])

    # Documentation
    ENABLE_DOCS: bool = Field(default=True)
    DOCS_URL: str = Field(default="/docs")
    REDOC_URL: str = Field(default="/redoc")

    # Monitoring
    ENABLE_METRICS: bool = Field(default=True)
    METRICS_PATH: str = Field(default="/metrics")

    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")
    LOG_FILE: Optional[str] = Field(default=None)

    # Storage
    STORAGE_TYPE: str = Field(default="local")
    STORAGE_PATH: str = Field(default="./storage")

    model_config = {"env_file": ".env", "case_sensitive": True}


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
