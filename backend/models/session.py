"""
Session Model

Tracks conversation sessions with expiry and state management.
Implements data-model.md Section 1: Session Table.
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional
import uuid


class Session(SQLModel, table=True):
    """
    Session table for tracking conversation sessions.

    State Transitions:
    - active → cleared (user triggers DELETE /history/{session_id})
    - active → expired (background job: last_activity + 24h < now())
    - cleared → [terminal state]
    - expired → [terminal state]
    """

    __tablename__ = "sessions"

    session_id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique session identifier (UUID v4)",
    )
    user_id: Optional[str] = Field(
        default=None,
        nullable=True,
        index=True,
        description="Optional user identifier (future: link to auth system)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Session creation timestamp (UTC)",
    )
    last_activity: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Last interaction timestamp (UTC), used for expiry",
    )
    state: str = Field(
        default="active",
        description="Session state: active | cleared | expired",
    )
    session_metadata: dict = Field(
        default={},
        sa_column=Column(JSON),
        description="Extensible metadata (e.g., user preferences, UI state)",
        alias="metadata"  # Keep API compatibility
    )

    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": None,
                "created_at": "2025-12-13T10:30:00Z",
                "last_activity": "2025-12-13T11:45:00Z",
                "state": "active",
                "session_metadata": {},
            }
        }


# Validation rules (enforced at API layer):
# - session_id: Must be valid UUID v4 format
# - state: Must be one of ["active", "cleared", "expired"]
# - last_activity: Must be >= created_at
# - metadata: Valid JSON object (enforced by PostgreSQL JSON column)
