"""
API Dependencies

Dependency injection for database sessions, rate limiting, and other shared resources.
"""

from fastapi import Depends, HTTPException, Request
from sqlmodel import Session
from typing import Generator, AsyncGenerator
from slowapi import Limiter
from slowapi.util import get_remote_address
from db.postgres import get_session as get_db_session
from rag.embedder import get_embedder
from rag.chunker import get_chunker
from rag.retriever import get_retriever
from rag.reranker import get_reranker
from utils.config import settings
from utils.logger import setup_logger, RequestLogger

# Authentication imports (Hackathon Bonus Feature 1)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi_users.db import SQLAlchemyUserDatabase
from models.user import User
from utils.user_manager import UserManager

logger = setup_logger(__name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=[settings.RATE_LIMIT],
)


def get_session() -> Generator[Session, None, None]:
    """
    Database session dependency.

    Yields a SQLModel session for database operations.
    Auto-commits on success, rolls back on errors.

    Usage:
        @router.get("/endpoint")
        async def endpoint(session: Session = Depends(get_session)):
            # Use session
            pass
    """
    yield from get_db_session()


def get_request_logger(request: Request) -> RequestLogger:
    """
    Request-scoped logger dependency.

    Creates a logger with correlation ID for the request.

    Usage:
        @router.post("/endpoint")
        async def endpoint(req_logger: RequestLogger = Depends(get_request_logger)):
            req_logger.info("Processing request", endpoint="/endpoint")
    """
    return RequestLogger(logger)


# RAG component dependencies (singleton pattern)


def get_embedder_dependency():
    """Dependency for embedder instance."""
    return get_embedder()


def get_chunker_dependency():
    """Dependency for chunker instance."""
    return get_chunker()


def get_retriever_dependency():
    """Dependency for retriever instance."""
    return get_retriever()


def get_reranker_dependency():
    """Dependency for reranker instance."""
    return get_reranker()


# Validation dependencies


def validate_session_state(session_id: str, db: Session = Depends(get_session)):
    """
    Validate that session exists and is in active state.

    Raises:
        HTTPException: If session not found or not active

    Usage:
        @router.post("/chat")
        async def chat(
            session_id: str,
            session_valid: None = Depends(validate_session_state)
        ):
            # Session is valid
            pass
    """
    from models.session import Session as SessionModel

    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    if session.state != "active":
        raise HTTPException(
            status_code=409,
            detail=f"Session is not active (state: {session.state})",
        )

    return session


# Rate limiting decorator helper


def get_rate_limiter():
    """
    Get rate limiter instance for manual use.

    Returns:
        Limiter: Slowapi limiter instance
    """
    return limiter


# Authentication dependencies (Hackathon Bonus Feature 1)

# Create async engine for FastAPI-Users using psycopg async
# psycopg3 supports async with the same postgresql+psycopg:// URL
async_database_url = settings.DATABASE_URL

# If using postgresql:// without driver, add psycopg driver
if "postgresql://" in async_database_url and "+" not in async_database_url:
    async_database_url = async_database_url.replace("postgresql://", "postgresql+psycopg://")

async_engine = create_async_engine(async_database_url)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session for FastAPI-Users.

    Yields:
        AsyncSession for user authentication operations
    """
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """
    User database dependency for FastAPI-Users.

    Args:
        session: Async database session

    Yields:
        SQLAlchemyUserDatabase configured for User model
    """
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """
    User manager dependency for FastAPI-Users.

    Args:
        user_db: User database adapter

    Yields:
        UserManager instance for handling authentication
    """
    yield UserManager(user_db)
