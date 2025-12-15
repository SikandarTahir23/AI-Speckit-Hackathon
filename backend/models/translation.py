"""
Translation Model (Hackathon Bonus Feature 3)

Stores Urdu translations of chapter content.
Implements caching strategy to minimize OpenAI API costs.
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, UniqueConstraint
from datetime import datetime
from typing import Optional


class Translation(SQLModel, table=True):
    """
    Translation table for caching Urdu translations of chapter content.

    Each record stores one chapter's translation to a specific language.
    Unique constraint ensures only one cached translation per (chapter_id, language_code).
    """

    __tablename__ = "translations"

    id: int = Field(
        primary_key=True,
        description="Unique translation entry identifier"
    )
    chapter_id: int = Field(
        index=True,
        description="Chapter identifier (1-8 for the 8 book chapters)"
    )
    language_code: str = Field(
        default="ur",
        max_length=10,
        description="ISO 639-1 language code (default: 'ur' for Urdu)"
    )
    original_text: str = Field(
        sa_column=Column(Text),
        description="Original English chapter content"
    )
    translated_text: str = Field(
        sa_column=Column(Text),
        description="AI-generated Urdu translation (preserves technical terms)"
    )
    cached_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Translation cache timestamp (UTC)"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "chapter_id": 3,
                "language_code": "ur",
                "original_text": "# Chapter 3: Actuation Systems\n\nActuators are devices that create movement...",
                "translated_text": "# باب 3: Actuation Systems\n\nActuators وہ آلات ہیں جو حرکت پیدا کرتے ہیں...",
                "cached_at": "2025-12-14T10:30:00Z"
            }
        }

    __table_args__ = (
        UniqueConstraint("chapter_id", "language_code", name="uix_chapter_language"),
    )


# Validation rules (enforced at API layer):
# - chapter_id: Integer 1-8 (8 chapters in the book)
# - language_code: ISO 639-1 format (2-10 chars, lowercase)
# - original_text: Non-empty string (validated before translation)
# - translated_text: Non-empty string (validated after OpenAI generation)
# - Unique constraint: Only one cached translation per (chapter_id, language_code)

# Performance characteristics (from plan.md):
# - Cache hit: < 2 seconds (SC-006)
# - Cache miss: < 15 seconds (includes OpenAI API call for translation)
# - Technical term preservation: Keep terms like "actuator", "ROS", "Python" untranslated (FR-022)
# - Pre-generation strategy: Create all 8 translations (8 chapters × 1 language) before demo
