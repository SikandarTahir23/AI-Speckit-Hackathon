# Data Model Design: RAG Chatbot

**Feature**: RAG Chatbot for "Physical AI & Humanoid Robotics Essentials"
**Date**: 2025-12-13
**Status**: Complete

## Overview

This document defines the data models for the RAG chatbot system, including PostgreSQL tables (SQLModel schemas), Qdrant vector collection structure, and validation rules. All entities align with constitutional requirements (Principle III: Data Integrity & Schema Consistency) and feature specification requirements.

---

## Entity Relationship Diagram

```
┌──────────────┐         ┌──────────────────┐
│   Session    │1      *│  ChatHistory     │
│──────────────│◄────────│──────────────────│
│ session_id PK│         │ id PK            │
│ created_at   │         │ session_id FK    │
│ last_activity│         │ query            │
│ state        │         │ answer           │
└──────────────┘         │ citations (JSON) │
                         │ timestamp        │
                         └──────────────────┘

┌──────────────┐         ┌──────────────────┐
│   Chapter    │1      *│   Paragraph      │
│──────────────│◄────────│──────────────────│
│ id PK        │         │ id PK            │
│ chapter_num  │         │ chapter_id FK    │
│ title        │         │ paragraph_index  │
│ summary      │         │ content          │
│ word_count   │         │ embedding_id     │◄─── References Qdrant point_id
└──────────────┘         │ metadata (JSON)  │
                         └──────────────────┘

┌─────────────────────────────────────────┐
│  Qdrant Collection: physical_ai_robotics│
│─────────────────────────────────────────│
│ point_id (UUID)                         │
│ vector [1536 dims]                      │
│ payload:                                │
│   - chunk_id                            │
│   - chapter_number                      │
│   - chapter_title                       │
│   - paragraph_index                     │
│   - content (text)                      │
│   - section_name                        │
│   - token_count                         │
└─────────────────────────────────────────┘
```

---

## PostgreSQL Tables (SQLModel Schemas)

### 1. Session Table

**Purpose**: Track conversation sessions with expiry and state management

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional
import uuid

class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    session_id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique session identifier (UUID v4)"
    )
    user_id: Optional[str] = Field(
        default=None,
        nullable=True,
        index=True,
        description="Optional user identifier (future: link to auth system)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Session creation timestamp (UTC)"
    )
    last_activity: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Last interaction timestamp (UTC), used for expiry"
    )
    state: str = Field(
        default="active",
        description="Session state: active | cleared | expired"
    )
    metadata: dict = Field(
        default={},
        sa_column=Column(JSON),
        description="Extensible metadata (e.g., user preferences, UI state)"
    )

    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": None,
                "created_at": "2025-12-13T10:30:00Z",
                "last_activity": "2025-12-13T11:45:00Z",
                "state": "active",
                "metadata": {}
            }
        }
```

**Validation Rules**:
- `session_id`: Must be valid UUID v4 format
- `state`: Must be one of `["active", "cleared", "expired"]` (Enum constraint)
- `last_activity`: Must be >= `created_at`
- `metadata`: Valid JSON object (enforced by PostgreSQL JSON column)

**Indexes**:
```sql
CREATE INDEX idx_session_last_activity ON sessions(last_activity);  -- For expiry cleanup
CREATE INDEX idx_session_user_id ON sessions(user_id) WHERE user_id IS NOT NULL;  -- For user session lookup
```

**State Transitions**:
```
active → cleared (user triggers DELETE /history/{session_id})
active → expired (background job: last_activity + 24h < now())
cleared → [terminal state]
expired → [terminal state]
```

---

### 2. ChatHistory Table

**Purpose**: Store conversation messages with Q&A pairs and citations

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import JSON, Text
from datetime import datetime
from typing import Optional, List
import uuid

class Citation(SQLModel):
    """Nested model for citations (not a table, used in JSON)"""
    chapter: str = Field(description="Chapter reference (e.g., 'Chapter 3: Actuation Systems')")
    section: Optional[str] = Field(default=None, description="Section reference (e.g., '3.2 Hydraulic Actuators')")
    paragraph: Optional[int] = Field(default=None, description="Paragraph index within chapter")

class ChatHistory(SQLModel, table=True):
    __tablename__ = "chat_history"

    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique message identifier"
    )
    session_id: str = Field(
        foreign_key="sessions.session_id",
        index=True,
        description="Reference to session (FK)"
    )
    query: str = Field(
        max_length=2000,
        sa_column=Column(Text),
        description="User question (max 2000 chars from research.md)"
    )
    answer: str = Field(
        sa_column=Column(Text),
        description="Chatbot answer (grounded in source material)"
    )
    citations: List[dict] = Field(
        default=[],
        sa_column=Column(JSON),
        description="List of citations (Citation model serialized to JSON)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Message creation timestamp (UTC)"
    )
    processing_time_ms: Optional[int] = Field(
        default=None,
        description="Query processing time in milliseconds (for performance monitoring)"
    )
    retrieval_score: Optional[float] = Field(
        default=None,
        description="Top retrieval score (cosine similarity) for confidence tracking"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "query": "What are hydraulic actuators used for in robotics?",
                "answer": "Hydraulic actuators are used in robotics for...",
                "citations": [
                    {"chapter": "Chapter 3: Actuation Systems", "section": "3.2 Hydraulic Actuators", "paragraph": 5}
                ],
                "timestamp": "2025-12-13T11:45:00Z",
                "processing_time_ms": 1850,
                "retrieval_score": 0.87
            }
        }
```

**Validation Rules**:
- `query`: Non-empty string, max 2000 characters (from research.md decision)
- `answer`: Non-empty string (enforced at API layer)
- `citations`: Valid JSON array of Citation objects
- `session_id`: Must reference existing session (FK constraint)
- `timestamp`: UTC ISO-8601 format
- `processing_time_ms`: Positive integer or null
- `retrieval_score`: Float between 0.0 and 1.0 or null

**Indexes**:
```sql
CREATE INDEX idx_chat_history_session ON chat_history(session_id);  -- For fetching conversation history
CREATE INDEX idx_chat_history_timestamp ON chat_history(timestamp DESC);  -- For chronological ordering
```

---

### 3. Chapter Table

**Purpose**: Store book chapter metadata for navigation and filtering

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from typing import Optional

class Chapter(SQLModel, table=True):
    __tablename__ = "chapters"

    id: int = Field(primary_key=True)
    chapter_number: int = Field(
        unique=True,
        index=True,
        description="Sequential chapter number (1, 2, 3...)"
    )
    title: str = Field(
        max_length=255,
        description="Chapter title (e.g., 'Actuation Systems')"
    )
    summary: Optional[str] = Field(
        default=None,
        description="Chapter summary (future: generated summaries)"
    )
    word_count: int = Field(
        default=0,
        description="Total word count for the chapter"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": 3,
                "chapter_number": 3,
                "title": "Actuation Systems",
                "summary": "This chapter covers hydraulic, electric, and pneumatic actuators...",
                "word_count": 5420
            }
        }
```

**Validation Rules**:
- `chapter_number`: Positive integer, unique across table
- `title`: Non-empty string, max 255 characters
- `word_count`: Non-negative integer

**Indexes**:
```sql
CREATE UNIQUE INDEX idx_chapter_number ON chapters(chapter_number);
```

---

### 4. Paragraph Table

**Purpose**: Store paragraph-level book content with Qdrant embedding references

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Text
from typing import Optional
import uuid

class Paragraph(SQLModel, table=True):
    __tablename__ = "paragraphs"

    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique paragraph identifier"
    )
    chapter_id: int = Field(
        foreign_key="chapters.id",
        index=True,
        description="Reference to chapter (FK)"
    )
    paragraph_index: int = Field(
        description="Sequential index within chapter (0, 1, 2...)"
    )
    content: str = Field(
        sa_column=Column(Text),
        description="Paragraph text content (chunked)"
    )
    embedding_id: str = Field(
        unique=True,
        description="Qdrant point ID (UUID) referencing vector embedding"
    )
    metadata: dict = Field(
        default={},
        sa_column=Column(JSON),
        description="Additional metadata (section_name, page_number, token_count)"
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
                    "char_count": 1950
                }
            }
        }
```

**Validation Rules**:
- `chapter_id`: Must reference existing chapter (FK constraint)
- `paragraph_index`: Non-negative integer
- `content`: Non-empty string
- `embedding_id`: Valid UUID, must match Qdrant point_id
- `metadata`: Valid JSON object

**Indexes**:
```sql
CREATE INDEX idx_paragraph_chapter ON paragraphs(chapter_id, paragraph_index);
CREATE UNIQUE INDEX idx_paragraph_embedding ON paragraphs(embedding_id);  -- For reverse lookup from Qdrant
```

---

## Qdrant Vector Collection

### Collection Configuration

**Collection Name**: `physical_ai_robotics_book`

**Vector Configuration**:
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, CollectionConfig

client = QdrantClient(url=os.getenv("QDRANT_URL"))

client.create_collection(
    collection_name="physical_ai_robotics_book",
    vectors_config=VectorParams(
        size=1536,  # text-embedding-3-small dimensions
        distance=Distance.COSINE  # Cosine similarity for semantic search
    ),
    hnsw_config={
        "m": 16,  # Number of edges per node (balanced accuracy/memory)
        "ef_construct": 100  # Construction time accuracy
    }
)
```

**Fallback Collection** (local embeddings):
```python
# If using MiniLM-L6-v2 (384 dims)
client.create_collection(
    collection_name="physical_ai_robotics_book_local",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
```

### Payload Schema

**Point Structure**:
```python
{
    "id": "880e8400-e29b-41d4-a716-446655440000",  # UUID (matches Paragraph.embedding_id)
    "vector": [0.123, -0.456, ...],  # 1536-dim embedding
    "payload": {
        "chunk_id": "770e8400-e29b-41d4-a716-446655440000",  # Paragraph.id
        "chapter_number": 3,
        "chapter_title": "Actuation Systems",
        "paragraph_index": 5,
        "content": "Hydraulic actuators provide high force density...",  # Full text for LLM context
        "section_name": "3.2 Hydraulic Actuators",
        "token_count": 487,
        "char_count": 1950,
        "page_number": 47  # Optional
    }
}
```

**Payload Field Types**:
- `chunk_id`: String (UUID)
- `chapter_number`: Integer (indexed for filtering)
- `chapter_title`: String (keyword)
- `paragraph_index`: Integer
- `content`: String (text, not indexed)
- `section_name`: String (keyword, optional)
- `token_count`: Integer
- `char_count`: Integer
- `page_number`: Integer (optional)

**Indexes** (Qdrant):
```python
# Create payload index for chapter filtering
client.create_payload_index(
    collection_name="physical_ai_robotics_book",
    field_name="chapter_number",
    field_schema="integer"
)

# Create payload index for section filtering (optional)
client.create_payload_index(
    collection_name="physical_ai_robotics_book",
    field_name="section_name",
    field_schema="keyword"
)
```

---

## Transient Models (Not Persisted)

### Query Model

**Purpose**: Input validation and preprocessing for chat requests

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class Query(BaseModel):
    """Transient model for query validation (not stored in DB)"""

    original_text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's original question"
    )
    normalized_text: Optional[str] = Field(
        default=None,
        description="Normalized query (lowercased, trimmed, etc.)"
    )
    conversation_context: Optional[list] = Field(
        default=None,
        description="Last 5 messages for follow-up question handling"
    )

    @validator('original_text')
    def validate_query(cls, v):
        # Remove leading/trailing whitespace
        v = v.strip()

        # Reject empty queries
        if not v:
            raise ValueError("Query cannot be empty or whitespace-only")

        # Check length
        if len(v) > 2000:
            raise ValueError(f"Query too long ({len(v)} chars). Maximum is 2000 characters.")

        return v

    def normalize(self):
        """Create normalized version of query"""
        self.normalized_text = self.original_text.lower().strip()
        return self
```

---

## Validation Rules Summary

### Cross-Entity Constraints

1. **Referential Integrity**:
   - `ChatHistory.session_id` → `Session.session_id` (FK, cascade delete)
   - `Paragraph.chapter_id` → `Chapter.id` (FK, restrict delete)
   - `Paragraph.embedding_id` ↔ Qdrant `point_id` (logical consistency, enforced at application layer)

2. **Timestamp Consistency**:
   - All timestamps in UTC ISO-8601 format
   - `Session.last_activity >= Session.created_at`
   - `ChatHistory.timestamp` should align with `Session.last_activity` (soft constraint)

3. **Citation Format**:
   ```python
   # Valid citation format (enforced at API layer)
   Citation(
       chapter="Chapter 3: Actuation Systems",  # Required
       section="3.2 Hydraulic Actuators",       # Optional
       paragraph=5                               # Optional
   )
   ```

4. **Character Limits**:
   - Query: 2000 chars (research.md decision)
   - Chapter title: 255 chars
   - Answer: No limit (can be verbose for complex questions)

5. **State Validation**:
   - Session state: Must be in `["active", "cleared", "expired"]`
   - Cannot add messages to `cleared` or `expired` sessions (enforced at API layer)

---

## Database Migration Strategy

### Alembic Setup

```python
# alembic.ini
[alembic]
script_location = backend/db/migrations
sqlalchemy.url = ${DATABASE_URL}  # From environment variable

# Initial migration
alembic revision --autogenerate -m "Initial schema: sessions, chat_history, chapters, paragraphs"
alembic upgrade head

# Schema versioning
Version 001: Initial tables
Version 002: Add processing_time_ms, retrieval_score to ChatHistory (future)
Version 003: Add user_level to Session (future personalization)
```

### Rollback Safety

All migrations must be reversible:
```python
def upgrade():
    # Forward migration
    op.add_column('chat_history', sa.Column('processing_time_ms', sa.Integer(), nullable=True))

def downgrade():
    # Rollback migration
    op.drop_column('chat_history', 'processing_time_ms')
```

---

## Data Integrity Checklist

- [x] All tables use SQLModel with explicit types
- [x] Foreign key relationships defined and enforced
- [x] Indexes created for query performance (session_id, timestamp, chapter_number)
- [x] Timestamps use UTC ISO-8601 format
- [x] JSON columns validated (citations, metadata)
- [x] Qdrant payload schema matches PostgreSQL metadata
- [x] UUIDs used for distributed ID generation (no auto-increment conflicts)
- [x] Validation rules documented for all fields
- [x] State transitions defined and enforced
- [x] Migration strategy defined with rollback support

---

## Next Steps

1. ✅ **Data Model Complete**: All entities defined with validation rules
2. **Phase 1**: Generate API contracts using these models
3. **Phase 1**: Generate quickstart.md with database initialization scripts
4. **Implementation**: Create SQLModel files in `backend/models/`
5. **Implementation**: Set up Alembic migrations in `backend/db/migrations/`

---

**Approved By**: Planning Agent
**Date**: 2025-12-13
**Ready for API Contract Generation**: ✅ Yes
