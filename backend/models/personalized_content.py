"""
PersonalizedContent Model (Hackathon Bonus Feature 2)

Stores AI-personalized chapter content for different difficulty levels.
Implements caching strategy to minimize OpenAI API costs.
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, UniqueConstraint, Enum as SQLAEnum
from datetime import datetime
from typing import Optional
import enum


class DifficultyLevel(str, enum.Enum):
    """Difficulty levels for personalized content"""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class PersonalizedContent(SQLModel, table=True):
    """
    PersonalizedContent table for caching AI-generated personalized chapter content.

    Each record stores one chapter's content adapted to a specific difficulty level.
    Unique constraint ensures only one cached version per (chapter_id, difficulty_level).
    """

    __tablename__ = "personalized_content"

    id: int = Field(
        primary_key=True,
        description="Unique cache entry identifier"
    )
    chapter_id: int = Field(
        index=True,
        description="Chapter identifier (1-8 for the 8 book chapters)"
    )
    difficulty_level: str = Field(
        sa_column=Column(SQLAEnum(DifficultyLevel)),
        description="Difficulty level for personalized content"
    )
    personalized_text: str = Field(
        sa_column=Column(Text),
        description="AI-generated personalized chapter content (full text)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Cache entry creation timestamp (UTC)"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "chapter_id": 3,
                "difficulty_level": "Beginner",
                "personalized_text": "# Chapter 3: Actuation Systems (Beginner)\n\nActuators are like the muscles of a robot...",
                "created_at": "2025-12-14T10:30:00Z"
            }
        }

    __table_args__ = (
        UniqueConstraint("chapter_id", "difficulty_level", name="uix_chapter_difficulty"),
    )


# Validation rules (enforced at API layer):
# - chapter_id: Integer 1-8 (8 chapters in the book)
# - difficulty_level: Must be one of ["Beginner", "Intermediate", "Advanced"]
# - personalized_text: Non-empty string (validated after OpenAI generation)
# - Unique constraint: Only one cached entry per (chapter_id, difficulty_level)

# Performance characteristics (from plan.md):
# - Cache hit: < 2 seconds (SC-004)
# - Cache miss: < 10 seconds (includes OpenAI API call)
# - Pre-generation strategy: Create all 24 entries (8 chapters × 3 levels) before demo
