"""Application configuration settings."""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    APP_NAME: str = "AURA - Autonomous Enterprise Intelligence Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Security & Auth
    SECRET_KEY: str = "aura-super-secret-production-grade-encryption-key-change-in-production-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./aura.db"
    
    # Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_FILE_EXTENSIONS: List[str] = [
        "pdf", "docx", "xlsx", "csv", "txt", "md", "html"
    ]
    
    # AI Engine & Provider
    AI_PROVIDER: str = "mock_local"  # "mock_local", "openai", "gemini", "anthropic"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    GEMINI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # RAG parameters
    EMBEDDING_DIMENSION: int = 384
    TOP_K_RETRIEVAL: int = 5
    HYBRID_ALPHA: float = 0.5  # Weight between dense vector (alpha) and BM25 (1 - alpha)
    SIMILARITY_THRESHOLD: float = 0.60
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    
    # MCP
    MCP_SERVER_HOST: str = "localhost"
    MCP_SERVER_PORT: int = 8001
    MCP_ENABLED: bool = True

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("./storage", exist_ok=True)
os.makedirs("./storage/reports", exist_ok=True)
