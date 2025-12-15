"""
ChatHistory Model

Stores conversation messages with Q&A pairs and citations.
Implements data-model.md Section 2: ChatHistory Table.
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Text
from datetime import datetime
from typing import Optional, List
import uuid


class Citation(SQLModel):
    """
    Nested model for citations (not a table, used in JSON).

    Serialized to JSON and stored in ChatHistory.citations field.
    """

    chapter: str = Field(
        description="Chapter reference (e.g., 'Chapter 3: Actuation Systems')"
    )
    section: Optional[str] = Field(
        default=None, description="Section reference (e.g., '3.2 Hydraulic Actuators')"
    )
    paragraph: Optional[int] = Field(
        default=None, description="Paragraph index within chapter"
    )


class ChatHistory(SQLModel, table=True):
    """
    ChatHistory table for storing conversation messages.

    Each record represents one Q&A exchange in a conversation session.
    Citations provide grounding in source material.
    """

    __tablename__ = "chat_history"

    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique message identifier",
    )
    session_id: str = Field(
        foreign_key="sessions.session_id",
        index=True,
        description="Reference to session (FK)",
    )
    query: str = Field(
        max_length=2000,
        sa_column=Column(Text),
        description="User question (max 2000 chars from research.md)",
    )
    answer: str = Field(
        sa_column=Column(Text),
        description="Chatbot answer (grounded in source material)",
    )
    citations: List[dict] = Field(
        default=[],
        sa_column=Column(JSON),
        description="List of citations (Citation model serialized to JSON)",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Message creation timestamp (UTC)",
    )
    processing_time_ms: Optional[int] = Field(
        default=None,
        description="Query processing time in milliseconds (for performance monitoring)",
    )
    retrieval_score: Optional[float] = Field(
        default=None,
        description="Top retrieval score (cosine similarity) for confidence tracking",
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "query": "What are hydraulic actuators used for in robotics?",
                "answer": "Hydraulic actuators are used in robotics for...",
                "citations": [
                    {
                        "chapter": "Chapter 3: Actuation Systems",
                        "section": "3.2 Hydraulic Actuators",
                        "paragraph": 5,
                    }
                ],
                "timestamp": "2025-12-13T11:45:00Z",
                "processing_time_ms": 1850,
                "retrieval_score": 0.87,
            }
        }


# Validation rules (enforced at API layer):
# - query: Non-empty string, max 2000 characters
# - answer: Non-empty string
# - citations: Valid JSON array of Citation objects
# - session_id: Must reference existing session (FK constraint)
# - timestamp: UTC ISO-8601 format
# - processing_time_ms: Positive integer or null
# - retrieval_score: Float between 0.0 and 1.0 or null
