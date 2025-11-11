"""
Settings module - Carrega e valida variáveis de ambiente
Centraliza configuração da aplicação usando pydantic-settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas de .env
    Utiliza pydantic para validação automática
    """
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./db.sqlite3"
    
    # S3/Storage (opcional para MVP)
    S3_ENDPOINT: Optional[str] = None
    S3_KEY: Optional[str] = None
    S3_SECRET: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    
    # Server config
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_ENV: str = "development"  # development | production
    
    # Security
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    MAX_UPLOAD_SIZE: int = 1_048_576  # 1MB
    
    # LLM Config
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_MAX_TOKENS: int = 500
    LLM_TEMPERATURE: float = 0.3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()
