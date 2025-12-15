"""
Book Models (Chapter and Paragraph)

Stores book chapter metadata and paragraph-level content with Qdrant embedding references.
Implements data-model.md Sections 3-4: Chapter and Paragraph Tables.
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Text
from typing import Optional
import uuid


class Chapter(SQLModel, table=True):
    """
    Chapter table for storing book chapter metadata.

    Used for navigation, filtering, and organizing book content.
    """

    __tablename__ = "chapters"

    id: int = Field(primary_key=True)
    chapter_number: int = Field(
        unique=True,
        index=True,
        description="Sequential chapter number (1, 2, 3...)",
    )
    title: str = Field(
        max_length=255, description="Chapter title (e.g., 'Actuation Systems')"
    )
    summary: Optional[str] = Field(
        default=None, description="Chapter summary (future: generated summaries)"
    )
    word_count: int = Field(
        default=0, description="Total word count for the chapter"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": 3,
                "chapter_number": 3,
                "title": "Actuation Systems",
                "summary": "This chapter covers hydraulic, electric, and pneumatic actuators...",
                "word_count": 5420,
            }
        }


class Paragraph(SQLModel, table=True):
    """
    Paragraph table for storing paragraph-level book content.

    Each paragraph is chunked (512 tokens) and has a corresponding embedding in Qdrant.
    The embedding_id field links to Qdrant point_id for vector search.
    """

    __tablename__ = "paragraphs"

    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique paragraph identifier",
    )
    chapter_id: int = Field(
        foreign_key="chapters.id",
        index=True,
        description="Reference to chapter (FK)",
    )
    paragraph_index: int = Field(
        description="Sequential index within chapter (0, 1, 2...)"
    )
    content: str = Field(
        sa_column=Column(Text), description="Paragraph text content (chunked)"
    )
    embedding_id: str = Field(
        unique=True,
        description="Qdrant point ID (UUID) referencing vector embedding",
    )
    para_metadata: dict = Field(
        default={},
        sa_column=Column(JSON),
        description="Additional metadata (section_name, page_number, token_count)",
        alias="metadata"  # Keep API compatibility
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "chapter_id": 3,
                "paragraph_index": 5,
                "content": "Hydraulic actuators provide high force density and are commonly used...",
                "embedding_id": "880e8400-e29b-41d4-a716-446655440000",
                "metadata": {
                    "section_name": "3.2 Hydraulic Actuators",
                    "page_number": 47,
                    "token_count": 487,
                    "char_count": 1950,
                },
            }
        }


# Validation rules (enforced at API layer):
# Chapter:
# - chapter_number: Positive integer, unique across table
# - title: Non-empty string, max 255 characters
# - word_count: Non-negative integer
#
# Paragraph:
# - chapter_id: Must reference existing chapter (FK constraint)
# - paragraph_index: Non-negative integer
# - content: Non-empty string
# - embedding_id: Valid UUID, must match Qdrant point_id
# - metadata: Valid JSON object
