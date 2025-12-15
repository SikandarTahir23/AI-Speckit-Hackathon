# Data Model: Hackathon Bonus Features

**Feature**: 002-hackathon-bonuses
**Date**: 2025-12-14
**Status**: Phase 1 Design
**Database**: Neon PostgreSQL (existing)
**ORM**: SQLModel

## Overview

This document defines the database schema for three bonus features: Authentication & User Profiling, Personalized Chapter Content, and Urdu Translation. All models extend the existing database schema and integrate with the current Session and ChatHistory tables.

## Entity Relationship Diagram

```
┌──────────────┐
│     User     │ (NEW - Authentication)
│──────────────│
│ PK id        │
│    email     │◄─────────┐
│    password  │          │
│    ...       │          │
└──────────────┘          │
        │                 │
        │ 1               │
        │                 │
        │ n               │
        ▼                 │
┌──────────────┐          │
│ UserProfile  │ (NEW)    │ FK user_id
│──────────────│          │
│ PK id        │          │
│ FK user_id   │──────────┘
│    software  │
│    hardware  │
│    familiar  │
└──────────────┘

┌──────────────┐          ┌──────────────┐
│   Chapter    │ (EXISTING│PersonalizedCo│ (NEW - Caching)
│──────────────│          │ntent         │
│ PK id        │◄─────────│──────────────│
│    number    │ 1      n │ PK id        │
│    title     │          │ FK chapter_id│
│    content   │          │    level     │
└──────────────┘          │    text      │
        │                 └──────────────┘
        │ 1
        │
        │ n
        ▼
┌──────────────┐
│ Translation  │ (NEW - Caching)
│──────────────│
│ PK id        │
│ FK chapter_id│
│    lang_code │
│    original  │
│    translated│
└──────────────┘
```

## Entities

### 1. User (NEW - Authentication)

**Purpose**: Stores user account information for authentication and personalization.

**Table Name**: `users`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `int` | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| `email` | `str` (255) | UNIQUE, NOT NULL, INDEXED | User email address (login identifier) |
| `hashed_password` | `str` (255) | NOT NULL | Bcrypt-hashed password |
| `is_active` | `bool` | DEFAULT TRUE | Account active status |
| `is_verified` | `bool` | DEFAULT FALSE | Email verification status |
| `software_background` | `str` (20) | NOT NULL, CHECK (value IN ('Beginner', 'Intermediate', 'Advanced')) | Software skill level (FR-001) |
| `hardware_background` | `str` (20) | NOT NULL, CHECK (value IN ('None', 'Basic', 'Hands-on')) | Hardware/robotics background (FR-001) |
| `python_familiar` | `bool` | DEFAULT FALSE | Familiarity with Python (FR-001) |
| `ros_familiar` | `bool` | DEFAULT FALSE | Familiarity with ROS/ROS2 (FR-001) |
| `aiml_familiar` | `bool` | DEFAULT FALSE | Familiarity with AI/ML (FR-001) |
| `created_at` | `datetime` | DEFAULT NOW(), INDEXED | Account creation timestamp (UTC) |
| `updated_at` | `datetime` | DEFAULT NOW(), ON UPDATE NOW() | Last profile update timestamp (UTC) |

**Indexes**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `email`
- INDEX: `created_at` (for user analytics)

**Validation Rules** (enforced at API layer):
- Email: Valid RFC 5322 email format
- Password: Minimum 8 characters, at least 1 uppercase, 1 lowercase, 1 digit (standard auth requirements)
- software_background: MUST be one of ['Beginner', 'Intermediate', 'Advanced']
- hardware_background: MUST be one of ['None', 'Basic', 'Hands-on']

**SQLModel Definition**:
```python
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Literal

class User(SQLAlchemyBaseUserTable[int], SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)

    # Profile fields (collected at signup - FR-001)
    software_background: Literal["Beginner", "Intermediate", "Advanced"] = Field(default="Beginner")
    hardware_background: Literal["None", "Basic", "Hands-on"] = Field(default="None")
    python_familiar: bool = Field(default=False)
    ros_familiar: bool = Field(default=False)
    aiml_familiar: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "email": "researcher@example.com",
                "hashed_password": "$2b$12$...",
                "is_active": True,
                "is_verified": False,
                "software_background": "Intermediate",
                "hardware_background": "Basic",
                "python_familiar": True,
                "ros_familiar": False,
                "aiml_familiar": True,
                "created_at": "2025-12-14T10:00:00Z",
                "updated_at": "2025-12-14T10:00:00Z"
            }
        }
```

**Relationships**:
- One-to-Many with ChatHistory (if chat is linked to users in future)
- Managed by FastAPI-Users library

---

### 2. PersonalizedContent (NEW - Caching)

**Purpose**: Caches personalized chapter content for different difficulty levels to reduce OpenAI API calls and improve response times.

**Table Name**: `personalized_content`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `int` | PRIMARY KEY, AUTO_INCREMENT | Unique cache entry identifier |
| `chapter_id` | `int` | FOREIGN KEY (chapters.id), NOT NULL, INDEXED | Reference to Chapter table |
| `difficulty_level` | `str` (20) | NOT NULL, CHECK (value IN ('Beginner', 'Intermediate', 'Advanced')) | Personalization level |
| `personalized_text` | `Text` | NOT NULL | AI-generated personalized chapter content |
| `created_at` | `datetime` | DEFAULT NOW(), INDEXED | Cache creation timestamp (UTC) |

**Indexes**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `(chapter_id, difficulty_level)` (one cached version per chapter+level combination)
- INDEX: `chapter_id` (for efficient lookups)
- INDEX: `created_at` (for cache analytics)

**Constraints**:
- UNIQUE constraint on `(chapter_id, difficulty_level)` ensures no duplicate cached entries
- FOREIGN KEY `chapter_id` → `chapters.id` ON DELETE CASCADE

**Validation Rules** (enforced at API layer):
- personalized_text: Maximum 100,000 characters (typical chapter is ~10,000 words = ~50,000 chars)
- difficulty_level: MUST be one of ['Beginner', 'Intermediate', 'Advanced']
- chapter_id: MUST reference existing Chapter

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Column, Text
from sqlalchemy import UniqueConstraint
from datetime import datetime
from typing import Literal

class PersonalizedContent(SQLModel, table=True):
    __tablename__ = "personalized_content"
    __table_args__ = (
        UniqueConstraint("chapter_id", "difficulty_level", name="uq_chapter_level"),
    )

    id: int = Field(primary_key=True)
    chapter_id: int = Field(foreign_key="chapters.id", index=True)
    difficulty_level: Literal["Beginner", "Intermediate", "Advanced"]
    personalized_text: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "chapter_id": 3,
                "difficulty_level": "Beginner",
                "personalized_text": "Simplified chapter content for beginners...",
                "created_at": "2025-12-14T10:00:00Z"
            }
        }
```

**Cache Strategy**:
- **On Request**: Check if cached entry exists for (chapter_id, difficulty_level); if yes, return immediately
- **Miss**: Generate via OpenAI, store in cache, return result
- **Pre-Generation**: Run batch script before hackathon demo to cache all 24 combinations (8 chapters × 3 levels)
- **Invalidation**: NOT needed for hackathon (book content is static); future enhancement: add `chapter_version` field

---

### 3. Translation (NEW - Caching)

**Purpose**: Caches Urdu translations of chapters to minimize OpenAI API calls and ensure consistent translation quality.

**Table Name**: `translations`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `int` | PRIMARY KEY, AUTO_INCREMENT | Unique translation entry identifier |
| `chapter_id` | `int` | FOREIGN KEY (chapters.id), NOT NULL, INDEXED | Reference to Chapter table |
| `language_code` | `str` (10) | NOT NULL, DEFAULT 'ur' | ISO 639-1 language code ('ur' for Urdu) |
| `original_text` | `Text` | NOT NULL | Original English chapter content (for reference) |
| `translated_text` | `Text` | NOT NULL | Urdu translation |
| `cached_at` | `datetime` | DEFAULT NOW(), INDEXED | Cache creation timestamp (UTC) |

**Indexes**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `(chapter_id, language_code)` (one translation per chapter+language)
- INDEX: `chapter_id` (for efficient lookups)
- INDEX: `cached_at` (for cache management)

**Constraints**:
- UNIQUE constraint on `(chapter_id, language_code)` ensures no duplicate translations
- FOREIGN KEY `chapter_id` → `chapters.id` ON DELETE CASCADE

**Validation Rules** (enforced at API layer):
- translated_text: Maximum 100,000 characters
- language_code: MUST be valid ISO 639-1 code (initially only 'ur' supported)
- original_text: MUST match current chapter content (for validation)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Column, Text
from sqlalchemy import UniqueConstraint
from datetime import datetime

class Translation(SQLModel, table=True):
    __tablename__ = "translations"
    __table_args__ = (
        UniqueConstraint("chapter_id", "language_code", name="uq_chapter_lang"),
    )

    id: int = Field(primary_key=True)
    chapter_id: int = Field(foreign_key="chapters.id", index=True)
    language_code: str = Field(default="ur", max_length=10)
    original_text: str = Field(sa_column=Column(Text))
    translated_text: str = Field(sa_column=Column(Text))
    cached_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "chapter_id": 3,
                "language_code": "ur",
                "original_text": "Hydraulic actuators provide high force density...",
                "translated_text": "ہائیڈرولک ایکچوایٹرز اعلیٰ قوت کی کثافت فراہم کرتے ہیں...",
                "cached_at": "2025-12-14T10:00:00Z"
            }
        }
```

**Cache Strategy**:
- **On Request**: Check if cached entry exists for (chapter_id, language_code); if yes, return immediately
- **Miss**: Generate via OpenAI translation API, store in cache, return result
- **Pre-Generation**: Run batch script before hackathon demo to cache all 8 chapters × 1 language = 8 entries
- **TTL**: No expiration (static book content); future enhancement: add `expires_at` field for dynamic content
- **Expected Hit Rate**: >90% (SC-010) - achievable since only 8 chapters exist

---

## Database Migration

**Migration File**: `backend/db/migrations/002_add_bonus_features.py`

```python
"""
Migration 002: Add bonus features tables (User, PersonalizedContent, Translation)

Adds:
- users table (authentication & user profiles)
- personalized_content table (chapter personalization cache)
- translations table (Urdu translation cache)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('software_background', sa.String(20), nullable=False),
        sa.Column('hardware_background', sa.String(20), nullable=False),
        sa.Column('python_familiar', sa.Boolean(), default=False),
        sa.Column('ros_familiar', sa.Boolean(), default=False),
        sa.Column('aiml_familiar', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create personalized_content table
    op.create_table(
        'personalized_content',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chapter_id', sa.Integer(), sa.ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('difficulty_level', sa.String(20), nullable=False),
        sa.Column('personalized_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, index=True),
    )
    op.create_unique_constraint('uq_chapter_level', 'personalized_content', ['chapter_id', 'difficulty_level'])

    # Create translations table
    op.create_table(
        'translations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chapter_id', sa.Integer(), sa.ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('language_code', sa.String(10), nullable=False, default='ur'),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('translated_text', sa.Text(), nullable=False),
        sa.Column('cached_at', sa.DateTime(), nullable=False, index=True),
    )
    op.create_unique_constraint('uq_chapter_lang', 'translations', ['chapter_id', 'language_code'])

def downgrade():
    op.drop_table('translations')
    op.drop_table('personalized_content')
    op.drop_table('users')
```

## Data Integrity Rules

### Referential Integrity
1. **PersonalizedContent.chapter_id** → **Chapter.id**: ON DELETE CASCADE (if chapter deleted, remove cached personalizations)
2. **Translation.chapter_id** → **Chapter.id**: ON DELETE CASCADE (if chapter deleted, remove cached translations)

### Uniqueness Constraints
1. **User.email**: Must be globally unique (prevents duplicate accounts)
2. **(PersonalizedContent.chapter_id, difficulty_level)**: One cached version per combination
3. **(Translation.chapter_id, language_code)**: One translation per combination

### Check Constraints
1. **User.software_background**: MUST be IN ('Beginner', 'Intermediate', 'Advanced')
2. **User.hardware_background**: MUST be IN ('None', 'Basic', 'Hands-on')
3. **PersonalizedContent.difficulty_level**: MUST be IN ('Beginner', 'Intermediate', 'Advanced')
4. **Translation.language_code**: MUST match ISO 639-1 format (2-character code)

## Performance Considerations

### Indexes
- **User.email**: Unique index for fast login lookups (O(log n))
- **PersonalizedContent (chapter_id, difficulty_level)**: Composite unique index for cache lookups
- **Translation (chapter_id, language_code)**: Composite unique index for translation lookups
- **created_at / cached_at**: Indexed for analytics and cache management queries

### Query Optimization
- Cache lookups use indexed unique constraints → O(1) performance
- Chapter-based queries use foreign key indexes
- Pre-generation eliminates need for real-time OpenAI API calls during demos

### Storage Estimates
- **User table**: ~500 bytes/row × 100 users = ~50 KB
- **PersonalizedContent table**: ~50 KB/row × 24 cached entries = ~1.2 MB
- **Translation table**: ~50 KB/row × 8 cached entries = ~400 KB
- **Total new storage**: ~1.7 MB (negligible in Neon PostgreSQL)

## Security Considerations

### Password Storage
- **Hashing**: Bcrypt with cost factor 12 (FastAPI-Users default)
- **Never store plaintext**: hashed_password field only
- **Salt**: Automatically handled by bcrypt

### Sensitive Data
- **Email**: Indexed but not public-facing
- **Profile data**: Non-sensitive (software/hardware background)
- **API keys**: NOT stored in database (use environment variables)

### SQL Injection Prevention
- **SQLModel parameterized queries**: All queries use bound parameters
- **No raw SQL**: ORM handles escaping

---

**Status**: Data model design complete. Ready for API contract definition.
