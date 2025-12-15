"""
PostgreSQL Database Connection and Session Management

Provides SQLModel engine, session dependency injection, and table creation.
Follows constitutional requirement III: Data Integrity & Schema Consistency.
"""

from sqlmodel import create_engine, SQLModel, Session, select
from typing import Generator
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Create database engine
# Connection pooling: max 5 connections, recycle after 3600s
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,  # Verify connections before using
)


def create_db_and_tables():
    """
    Create all database tables.

    Called during application startup or via Alembic migrations.
    Uses SQLModel metadata to create tables from model definitions.
    """
    # Import all models first so SQLModel can discover them
    from models.session import Session
    from models.chat import ChatHistory
    from models.book import Chapter, Paragraph

    logger.info("Creating database tables")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def get_session() -> Generator[Session, None, None]:
    """
    Dependency injection for database sessions.

    Yields a SQLModel session for use in FastAPI route dependencies.
    Automatically commits on success and rolls back on errors.

    Usage:
        @app.get("/endpoint")
        async def endpoint(session: Session = Depends(get_session)):
            # Use session for database operations
            pass
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()


def check_connection() -> bool:
    """
    Health check for PostgreSQL connection.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        from sqlalchemy import text
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        return False


def insert_chapters(chapters_data: list, session: Session) -> list:
    """
    Insert chapter records into database.

    Args:
        chapters_data: List of chapter dictionaries with chapter_number, title, word_count
        session: SQLModel database session

    Returns:
        List of created Chapter objects with IDs

    Example input:
        [
            {"chapter_number": 1, "title": "Introduction", "word_count": 1500},
            ...
        ]
    """
    from models.book import Chapter

    created_chapters = []

    for ch_data in chapters_data:
        # Check if chapter already exists
        existing = session.exec(
            select(Chapter).where(Chapter.chapter_number == ch_data['chapter_number'])
        ).first()

        if existing:
            logger.info(f"Chapter {ch_data['chapter_number']} already exists, skipping")
            created_chapters.append(existing)
            continue

        # Create new chapter
        chapter = Chapter(
            chapter_number=ch_data["chapter_number"],
            title=ch_data["title"],
            word_count=ch_data.get("word_count", 0),
        )
        session.add(chapter)
        session.flush()  # Get ID without committing
        created_chapters.append(chapter)
        logger.info(f"Inserted chapter {chapter.chapter_number}: {chapter.title} (ID: {chapter.id})")

    session.commit()
    logger.info(f"Inserted {len(created_chapters)} chapters")

    return created_chapters


def insert_paragraphs(paragraphs_data: list, session: Session) -> list:
    """
    Insert paragraph records into database.

    Args:
        paragraphs_data: List of paragraph dictionaries with chapter_id, paragraph_index, content, embedding_id, metadata
        session: SQLModel database session

    Returns:
        List of created Paragraph objects with IDs

    Example input:
        [
            {
                "chapter_id": 1,
                "paragraph_index": 0,
                "content": "This is the first paragraph...",
                "embedding_id": "880e8400-e29b-41d4-a716-446655440000",
                "para_metadata": {"section_name": "1.1 Overview", "token_count": 487}
            },
            ...
        ]
    """
    from models.book import Paragraph

    created_paragraphs = []

    for para_data in paragraphs_data:
        paragraph = Paragraph(
            chapter_id=para_data["chapter_id"],
            paragraph_index=para_data["paragraph_index"],
            content=para_data["content"],
            embedding_id=para_data["embedding_id"],
            para_metadata=para_data.get("para_metadata", {}),
        )
        session.add(paragraph)
        created_paragraphs.append(paragraph)

    session.commit()
    logger.info(f"Inserted {len(created_paragraphs)} paragraphs")

    return created_paragraphs


# Connection test on module import
try:
    from sqlalchemy import text
    with Session(engine) as session:
        result = session.exec(text("SELECT version()"))
        version = result.one()
        logger.info(f"Connected to PostgreSQL: {version}")
except Exception as e:
    logger.warning(f"Failed to connect to PostgreSQL on startup: {e}")
    logger.warning("Application will continue, but database operations will fail")
