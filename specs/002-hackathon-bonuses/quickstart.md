# Quickstart Guide: Hackathon Bonus Features

**Feature**: 002-hackathon-bonuses
**Target Audience**: Developers implementing or testing the bonus features
**Estimated Setup Time**: 30-45 minutes

## Prerequisites

Before starting, ensure you have:

✅ Existing RAG chatbot system running (see main README.md)
✅ Python 3.11+ installed
✅ Node.js 20+ installed (for Docusaurus frontend)
✅ Neon PostgreSQL database accessible
✅ OpenAI API key with GPT-3.5-turbo access
✅ Docker Desktop (optional, for containerized deployment)

## Overview

This guide walks you through setting up three hackathon bonus features:

1. **Authentication** (50 pts) - User signup/signin with profile collection
2. **Personalization** (50 pts) - AI-powered chapter content adaptation
3. **Translation** (25 pts) - Urdu translation with caching

**Total Implementation Time**: 10-12 hours

## Architecture Overview

```
Frontend (Docusaurus/React)
    ↓
FastAPI Backend
    ├─ FastAPI-Users (Authentication)
    ├─ OpenAI API (Personalization & Translation)
    └─ Neon PostgreSQL
        ├─ users (authentication & profiles)
        ├─ personalized_content (cache)
        └─ translations (cache)
```

## Step 1: Backend Setup (2-3 hours)

### 1.1 Install Dependencies

```bash
cd backend

# Add to requirements.txt
echo "fastapi-users[sqlalchemy]==12.1.2" >> requirements.txt
echo "python-jose[cryptography]==3.3.0" >> requirements.txt
echo "passlib[bcrypt]==1.7.4" >> requirements.txt

# Install
pip install -r requirements.txt
```

### 1.2 Update Environment Variables

```bash
# backend/.env
DATABASE_URL=postgresql://user:password@db.neon.tech/rag_chatbot
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
OPENAI_API_KEY=sk-your-openai-api-key

# Authentication settings
SESSION_MAX_AGE=604800  # 7 days (persistent sessions)
PASSWORD_MIN_LENGTH=8
```

### 1.3 Run Database Migration

```bash
cd backend

# Generate migration
alembic revision --autogenerate -m "Add bonus features tables"

# Review migration file in backend/db/migrations/
# Ensure users, personalized_content, and translations tables are created

# Apply migration
alembic upgrade head

# Verify tables exist
psql $DATABASE_URL -c "\dt"
# Should see: users, personalized_content, translations
```

### 1.4 Test Database Connection

```python
# backend/test_db.py
from db.postgres import get_session
from models.user import User

async def test_connection():
    async for session in get_session():
        # Test User table
        user = User(
            email="test@example.com",
            hashed_password="$2b$12$test",
            software_background="Beginner",
            hardware_background="None"
        )
        session.add(user)
        await session.commit()
        print(f"✅ User created: {user.id}")

        # Clean up
        await session.delete(user)
        await session.commit()
        print("✅ Database connection successful")

# Run test
import asyncio
asyncio.run(test_connection())
```

## Step 2: Authentication Implementation (2-3 hours)

### 2.1 Create User Model

```python
# backend/models/user.py
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Literal

class User(SQLAlchemyBaseUserTable[int], SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)

    # Profile fields (FR-001)
    software_background: Literal["Beginner", "Intermediate", "Advanced"] = Field(default="Beginner")
    hardware_background: Literal["None", "Basic", "Hands-on"] = Field(default="None")
    python_familiar: bool = Field(default=False)
    ros_familiar: bool = Field(default=False)
    aiml_familiar: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2.2 Configure FastAPI-Users

```python
# backend/utils/auth.py
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend, JWTStrategy
from models.user import User
from utils.config import settings

# Cookie transport (persistent sessions)
cookie_transport = CookieTransport(
    cookie_name="session",
    cookie_max_age=settings.SESSION_MAX_AGE,
    cookie_httponly=True,
    cookie_secure=False,  # Set True in production (HTTPS)
    cookie_samesite="lax"
)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=settings.SESSION_MAX_AGE)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,  # Defined in user_manager.py
    [auth_backend],
)

# Export auth dependency
current_user = fastapi_users.current_user()
```

### 2.3 Add Authentication Routes

```python
# backend/api/routes.py (extend existing file)
from fastapi import APIRouter
from utils.auth import fastapi_users, auth_backend
from models.user import User
from pydantic import BaseModel

router = APIRouter()

# Existing routes...

# Authentication routes
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Authentication"],
)

router.include_router(
    fastapi_users.get_register_router(User, UserRead),
    prefix="/auth",
    tags=["Authentication"],
)

# Profile endpoint
@router.get("/auth/me", response_model=UserRead)
async def get_current_user(user: User = Depends(current_user)):
    return user
```

### 2.4 Test Authentication

```bash
# Start backend
cd backend
uvicorn main:app --reload --port 8000

# Test signup
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "software_background": "Intermediate",
    "hardware_background": "Basic",
    "python_familiar": true,
    "ros_familiar": false,
    "aiml_familiar": true
  }'

# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePass123!"}'

# Test profile (use session cookie from login)
curl http://localhost:8000/auth/me -H "Cookie: session=<cookie-from-login>"
```

## Step 3: Personalization Implementation (2-3 hours)

### 3.1 Create PersonalizedContent Model

```python
# backend/models/personalized_content.py
from sqlmodel import SQLModel, Field, Column, Text
from sqlalchemy import UniqueConstraint
from datetime import datetime
from typing import Literal

class PersonalizedContent(SQLModel, table=True):
    __tablename__ = "personalized_content"
    __table_args__ = (UniqueConstraint("chapter_id", "difficulty_level", name="uq_chapter_level"),)

    id: int = Field(primary_key=True)
    chapter_id: int = Field(foreign_key="chapters.id", index=True)
    difficulty_level: Literal["Beginner", "Intermediate", "Advanced"]
    personalized_text: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3.2 Create Personalization Agent

```python
# backend/agents/personalization_agent.py
from openai import AsyncOpenAI
from utils.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

PROMPTS = {
    "Beginner": """
You are rewriting a technical chapter on Physical AI and Robotics for beginner learners.
GOAL: Simplify language while preserving ALL technical facts.
RULES:
1. Replace jargon with plain language
2. Add analogies and examples
3. Break complex sentences into shorter ones
4. NEVER add information not in original text
5. Preserve all formulas and citations

Original Chapter Content:
{content}

Rewrite for absolute beginners:
""",
    "Intermediate": """
You are rewriting for intermediate learners with basic robotics knowledge.
GOAL: Balance technical depth with accessibility.
RULES:
1. Use technical terms without over-explaining
2. Moderate sentence complexity
3. NEVER add information not in original text

Original Chapter Content:
{content}

Rewrite for intermediate learners:
""",
    "Advanced": """
You are rewriting for advanced practitioners.
GOAL: Increase technical density and reduce verbosity.
RULES:
1. Use advanced terminology without definitions
2. Condense explanations
3. NEVER add information not in original text

Original Chapter Content:
{content}

Rewrite for experts:
"""
}

async def personalize_content(content: str, difficulty_level: str) -> str:
    prompt = PROMPTS[difficulty_level].format(content=content)

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,  # Lower temperature for consistency
        max_tokens=4096
    )

    return response.choices[0].message.content
```

### 3.3 Add Personalization Endpoint

```python
# backend/api/routes.py (extend)
from models.personalized_content import PersonalizedContent
from agents.personalization_agent import personalize_content
from sqlmodel import Session, select
import time

@router.post("/personalize", tags=["Personalization"])
async def personalize_chapter(
    request: PersonalizationRequest,
    user: User = Depends(current_user),
    session: Session = Depends(get_session)
):
    start_time = time.time()

    # Check cache
    cached = session.exec(
        select(PersonalizedContent).where(
            PersonalizedContent.chapter_id == request.chapter_id,
            PersonalizedContent.difficulty_level == request.difficulty_level
        )
    ).first()

    if cached:
        processing_time = int((time.time() - start_time) * 1000)
        return {
            "chapter_id": request.chapter_id,
            "personalized_content": cached.personalized_text,
            "cached": True,
            "processing_time_ms": processing_time
        }

    # Generate
    chapter = session.get(Chapter, request.chapter_id)
    personalized = await personalize_content(chapter.content, request.difficulty_level)

    # Cache
    cached_entry = PersonalizedContent(
        chapter_id=request.chapter_id,
        difficulty_level=request.difficulty_level,
        personalized_text=personalized
    )
    session.add(cached_entry)
    session.commit()

    processing_time = int((time.time() - start_time) * 1000)
    return {
        "chapter_id": request.chapter_id,
        "personalized_content": personalized,
        "cached": False,
        "processing_time_ms": processing_time
    }
```

### 3.4 Test Personalization

```bash
# Test endpoint
curl -X POST http://localhost:8000/personalize \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<session-cookie>" \
  -d '{"chapter_id": 1, "difficulty_level": "Beginner"}'

# Verify caching (second request should be <2s)
time curl -X POST http://localhost:8000/personalize \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<session-cookie>" \
  -d '{"chapter_id": 1, "difficulty_level": "Beginner"}'
```

## Step 4: Translation Implementation (1-2 hours)

### 4.1 Create Translation Model

```python
# backend/models/translation.py
from sqlmodel import SQLModel, Field, Column, Text
from sqlalchemy import UniqueConstraint
from datetime import datetime

class Translation(SQLModel, table=True):
    __tablename__ = "translations"
    __table_args__ = (UniqueConstraint("chapter_id", "language_code", name="uq_chapter_lang"),)

    id: int = Field(primary_key=True)
    chapter_id: int = Field(foreign_key="chapters.id", index=True)
    language_code: str = Field(default="ur")
    original_text: str = Field(sa_column=Column(Text))
    translated_text: str = Field(sa_column=Column(Text))
    cached_at: datetime = Field(default_factory=datetime.utcnow)
```

### 4.2 Create Translation Agent

```python
# backend/agents/translation_agent.py
from openai import AsyncOpenAI
from utils.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

TRANSLATION_PROMPT = """
Translate the following technical text about Physical AI and Robotics from English into Urdu.

RULES:
1. Preserve technical terms in English when no direct Urdu equivalent (e.g., "actuator", "kinematics")
2. Maintain all numerical values, formulas, and citations exactly
3. Use formal/academic Urdu for technical content
4. NEVER omit information from original text

Original Text (English):
{content}

Provide complete Urdu translation:
"""

async def translate_to_urdu(content: str) -> str:
    prompt = TRANSLATION_PROMPT.format(content=content)

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=4096
    )

    return response.choices[0].message.content
```

### 4.3 Add Translation Endpoint

```python
# backend/api/routes.py (extend)
from models.translation import Translation
from agents.translation_agent import translate_to_urdu

@router.post("/translate", tags=["Translation"])
async def translate_chapter(
    request: TranslationRequest,
    session: Session = Depends(get_session)
):
    start_time = time.time()

    # Check cache
    cached = session.exec(
        select(Translation).where(
            Translation.chapter_id == request.chapter_id,
            Translation.language_code == request.target_lang
        )
    ).first()

    if cached:
        processing_time = int((time.time() - start_time) * 1000)
        return {
            "chapter_id": request.chapter_id,
            "original": cached.original_text,
            "translated": cached.translated_text,
            "cached": True,
            "processing_time_ms": processing_time
        }

    # Generate translation
    chapter = session.get(Chapter, request.chapter_id)
    translated = await translate_to_urdu(chapter.content)

    # Cache
    translation = Translation(
        chapter_id=request.chapter_id,
        language_code=request.target_lang,
        original_text=chapter.content,
        translated_text=translated
    )
    session.add(translation)
    session.commit()

    processing_time = int((time.time() - start_time) * 1000)
    return {
        "chapter_id": request.chapter_id,
        "original": chapter.content,
        "translated": translated,
        "cached": False,
        "processing_time_ms": processing_time
    }
```

### 4.4 Test Translation

```bash
# Test endpoint
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"chapter_id": 1, "target_lang": "ur"}'

# Verify cache hit rate (run 10 times, should only generate once)
for i in {1..10}; do
  curl -X POST http://localhost:8000/translate \
    -H "Content-Type: application/json" \
    -d '{"chapter_id": 1, "target_lang": "ur"}' -s | jq '.cached'
done
# Expected: first request cached=false, next 9 requests cached=true
```

## Step 5: Frontend Integration (3-4 hours)

### 5.1 Create AuthWidget Component

```bash
cd src/components
mkdir AuthWidget
```

```tsx
// src/components/AuthWidget/index.tsx
import React, { useState } from 'react';
import styles from './styles.module.css';

export default function AuthWidget() {
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [profile, setProfile] = useState({
    software_background: 'Beginner',
    hardware_background: 'None',
    python_familiar: false,
    ros_familiar: false,
    aiml_familiar: false,
  });

  const handleSignup = async () => {
    const response = await fetch('http://localhost:8000/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, ...profile }),
      credentials: 'include',
    });
    // Handle response...
  };

  return (
    <div className={styles.authWidget}>
      {/* Signup/Signin form implementation */}
    </div>
  );
}
```

### 5.2 Create ChapterControls Component

```tsx
// src/components/ChapterControls/index.tsx
import React, { useState } from 'react';

interface ChapterControlsProps {
  chapterId: number;
  onPersonalize: (content: string) => void;
  onTranslate: (urdu: string, english: string) => void;
}

export default function ChapterControls({ chapterId, onPersonalize, onTranslate }: ChapterControlsProps) {
  const [loading, setLoading] = useState(false);

  const handlePersonalize = async (level: string) => {
    setLoading(true);
    const response = await fetch('http://localhost:8000/personalize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: chapterId, difficulty_level: level }),
      credentials: 'include',
    });
    const data = await response.json();
    onPersonalize(data.personalized_content);
    setLoading(false);
  };

  const handleTranslate = async () => {
    setLoading(true);
    const response = await fetch('http://localhost:8000/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: chapterId, target_lang: 'ur' }),
    });
    const data = await response.json();
    onTranslate(data.translated, data.original);
    setLoading(false);
  };

  return (
    <div>
      <button onClick={() => handlePersonalize('Beginner')}>Beginner</button>
      <button onClick={() => handlePersonalize('Intermediate')}>Intermediate</button>
      <button onClick={() => handlePersonalize('Advanced')}>Advanced</button>
      <button onClick={handleTranslate}>Translate to Urdu</button>
    </div>
  );
}
```

## Step 6: Pre-Generation Script (hackathon prep)

### 6.1 Create Pre-Generation Script

```python
# backend/scripts/pre_generate_cache.py
import asyncio
from db.postgres import get_session
from models.chapter import Chapter
from models.personalized_content import PersonalizedContent
from models.translation import Translation
from agents.personalization_agent import personalize_content
from agents.translation_agent import translate_to_urdu

async def pre_generate_all():
    async for session in get_session():
        chapters = session.exec(select(Chapter)).all()
        levels = ["Beginner", "Intermediate", "Advanced"]

        print(f"Pre-generating content for {len(chapters)} chapters...")

        # Personalization
        for chapter in chapters:
            for level in levels:
                existing = session.exec(
                    select(PersonalizedContent).where(
                        PersonalizedContent.chapter_id == chapter.id,
                        PersonalizedContent.difficulty_level == level
                    )
                ).first()

                if not existing:
                    print(f"Personalizing Chapter {chapter.chapter_number} - {level}...")
                    personalized = await personalize_content(chapter.content, level)
                    session.add(PersonalizedContent(
                        chapter_id=chapter.id,
                        difficulty_level=level,
                        personalized_text=personalized
                    ))
                    session.commit()
                    print(f"✅ Cached Chapter {chapter.chapter_number} - {level}")
                else:
                    print(f"⏭️ Skipping Chapter {chapter.chapter_number} - {level} (already cached)")

        # Translation
        for chapter in chapters:
            existing = session.exec(
                select(Translation).where(
                    Translation.chapter_id == chapter.id,
                    Translation.language_code == "ur"
                )
            ).first()

            if not existing:
                print(f"Translating Chapter {chapter.chapter_number} to Urdu...")
                translated = await translate_to_urdu(chapter.content)
                session.add(Translation(
                    chapter_id=chapter.id,
                    language_code="ur",
                    original_text=chapter.content,
                    translated_text=translated
                ))
                session.commit()
                print(f"✅ Cached Chapter {chapter.chapter_number} Urdu translation")
            else:
                print(f"⏭️ Skipping Chapter {chapter.chapter_number} translation (already cached)")

        print("🎉 Pre-generation complete! All content cached for demo.")

if __name__ == "__main__":
    asyncio.run(pre_generate_all())
```

### 6.2 Run Pre-Generation (before demo)

```bash
cd backend
python scripts/pre_generate_cache.py

# Expected output:
# Pre-generating content for 8 chapters...
# Personalizing Chapter 1 - Beginner...
# ✅ Cached Chapter 1 - Beginner
# ... (24 personalized versions + 8 translations = 32 total)
# 🎉 Pre-generation complete!

# Verify cache coverage
curl http://localhost:8000/personalize/status
curl http://localhost:8000/translate/status
```

## Hackathon Judge Testing Guide

### Test Flow for Judges (5-10 minutes)

**Test 1: Authentication (FR-001 to FR-009)**
1. Visit website → Click "Sign Up"
2. Fill profile questions → Submit
3. Close browser → Reopen → Verify still logged in (SC-002)

**Test 2: Personalization (FR-010 to FR-017)**
1. Navigate to Chapter 3
2. Select "Beginner" → Observe simplified content
3. Select "Advanced" → Observe technical content
4. Verify <2s response time (cached) (SC-003, SC-004)

**Test 3: Translation (FR-018 to FR-026)**
1. Click "Translate to Urdu" on Chapter 3
2. Verify side-by-side English + Urdu display
3. Verify <2s response time (cached) (SC-004)

**Expected Results**:
- ✅ All 3 features working independently
- ✅ Persistent login across browser restarts
- ✅ Fast responses (<2s for cached content)
- ✅ Graceful error handling

## Troubleshooting

### Issue: Authentication cookie not persisting
**Solution**: Check `cookie_secure=False` in development, ensure SameSite="lax"

### Issue: OpenAI API rate limits during demo
**Solution**: Run pre-generation script beforehand to cache all content

### Issue: Translation shows English technical terms
**Expected behavior**: Prompt instructs preservation of terms like "actuator", "kinematics"

### Issue: Personalization not significantly different
**Solution**: Review and refine prompts in `personalization_agent.py`

## Next Steps

After completing this quickstart:

1. ✅ Run pre-generation script
2. ✅ Test all three features end-to-end
3. ✅ Verify cache hit rates (>90% per SC-010)
4. ✅ Prepare hackathon judge testing checklist
5. ✅ Deploy to production environment (optional)

---

**Questions or issues?** See [data-model.md](./data-model.md) for detailed schema documentation, or [contracts/](./contracts/) for API specifications.

**Ready for tasks?** Run `/sp.tasks` to generate implementation task breakdown.
