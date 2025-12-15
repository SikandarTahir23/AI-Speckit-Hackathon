"""
Configuration Management

Loads environment variables using Pydantic BaseSettings.
All configuration is validated and type-safe.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = Field(default="RAG Chatbot", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    ENVIRONMENT: str = Field(default="development", description="Environment (development/production)")

    # Database
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string (e.g., postgresql://user:pass@localhost:5432/db)"
    )

    # Vector Database
    QDRANT_URL: str = Field(
        default="http://localhost:6333",
        description="Qdrant vector database URL"
    )
    QDRANT_API_KEY: str = Field(
        default=None,
        description="Qdrant API key (required for Qdrant Cloud)"
    )

    # OpenAI API
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    LLM_MODEL: str = Field(
        default="gpt-4o-mini",
        description="OpenAI LLM model for answer generation"
    )
    RETRIEVAL_CONFIDENCE_THRESHOLD: float = Field(
        default=0.7,
        description="Minimum confidence score to return answer (vs fallback)"
    )

    # Google Gemini API (for translation)
    GEMINI_API_KEY: str = Field(default=None, description="Google Gemini API key for translation")

    # Embedding Configuration
    EMBEDDING_MODEL: str = Field(
        default="openai",
        description="Embedding model: 'openai' (text-embedding-3-small) or 'local' (MiniLM)"
    )

    @validator("EMBEDDING_MODEL")
    def validate_embedding_model(cls, v):
        """Validate embedding model choice"""
        if v not in ["openai", "local"]:
            raise ValueError("EMBEDDING_MODEL must be 'openai' or 'local'")
        return v

    # Rate Limiting
    REDIS_URL: str = Field(
        default="memory://",
        description="Redis URL for rate limiting (use memory:// for dev)"
    )
    RATE_LIMIT: str = Field(
        default="20/minute",
        description="Rate limit (e.g., '20/minute', '100/hour')"
    )

    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()

    # Book Path
    BOOK_PATH: str = Field(
        default="/app/data/book_source/physical_ai_robotics.md",
        description="Path to book content file"
    )

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )

    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins string into list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Session Settings
    SESSION_EXPIRY_HOURS: int = Field(
        default=24,
        description="Session expiry time in hours"
    )

    # Authentication Settings (Hackathon Bonus Feature 1)
    SECRET_KEY: str = Field(
        ...,
        description="Secret key for JWT token generation (generate with: openssl rand -hex 32)"
    )
    SESSION_MAX_AGE: int = Field(
        default=604800,
        description="Session max age in seconds (default: 7 days)"
    )
    PASSWORD_MIN_LENGTH: int = Field(
        default=8,
        description="Minimum password length for user registration"
    )

    @validator("PASSWORD_MIN_LENGTH")
    def validate_password_min_length(cls, v):
        """Validate password minimum length"""
        if v < 6 or v > 128:
            raise ValueError("PASSWORD_MIN_LENGTH must be between 6 and 128")
        return v

    # Chunking Configuration
    CHUNK_SIZE: int = Field(
        default=512,
        description="Target chunk size in tokens"
    )
    CHUNK_OVERLAP: int = Field(
        default=50,
        description="Chunk overlap in tokens"
    )

    @validator("CHUNK_SIZE")
    def validate_chunk_size(cls, v):
        """Validate chunk size is reasonable"""
        if v < 100 or v > 1000:
            raise ValueError("CHUNK_SIZE must be between 100 and 1000 tokens")
        return v

    @validator("CHUNK_OVERLAP")
    def validate_chunk_overlap(cls, v):
        """Validate chunk overlap is reasonable"""
        if v < 0 or v > 200:
            raise ValueError("CHUNK_OVERLAP must be between 0 and 200 tokens")
        return v

    # Retrieval Configuration
    RETRIEVAL_TOP_K: int = Field(
        default=10,
        description="Number of chunks to retrieve from Qdrant"
    )
    RERANK_TOP_N: int = Field(
        default=5,
        description="Number of chunks to keep after reranking"
    )
    RETRIEVAL_SCORE_THRESHOLD: float = Field(
        default=0.7,
        description="Minimum retrieval score for confidence (0.0-1.0)"
    )

    @validator("RETRIEVAL_SCORE_THRESHOLD")
    def validate_retrieval_threshold(cls, v):
        """Validate retrieval score threshold"""
        if v < 0.0 or v > 1.0:
            raise ValueError("RETRIEVAL_SCORE_THRESHOLD must be between 0.0 and 1.0")
        return v

    class Config:
        """Pydantic config"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
