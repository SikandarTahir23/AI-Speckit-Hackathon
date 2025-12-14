"""
API Routes

FastAPI router registration and error handler setup.
Includes authentication endpoints (Hackathon Bonus Feature 1).
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from utils.logger import setup_logger

# Authentication imports (Hackathon Bonus Feature 1)
from fastapi_users import FastAPIUsers, schemas
from models.user import User, SoftwareBackground, HardwareBackground
from utils.auth import auth_backend
from api.dependencies import get_user_manager
from pydantic import BaseModel, EmailStr, Field as PydField
from typing import Optional

logger = setup_logger(__name__)

# Create API router
router = APIRouter()

# Note: Exception handlers are registered on the main FastAPI app in main.py,
# not on routers. APIRouter doesn't support exception_handler decorator.


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns service status and dependencies health.
    Will be fully implemented in Phase 8 (T060).
    """
    return {
        "status": "healthy",
        "service": "RAG Chatbot API",
        "version": "1.0.0",
    }


# ====================
# Authentication Schemas & Routes (Hackathon Bonus Feature 1)
# ====================

# T021: Pydantic request/response schemas with profile fields

class UserRead(BaseModel):
    """
    User response schema (returned after login/registration).

    Includes authentication fields and profile data.
    """
    id: int
    email: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    software_background: str
    hardware_background: str
    python_familiar: bool
    ros_familiar: bool
    aiml_familiar: bool

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """
    User registration schema (required fields for signup).

    Extends base authentication with profile questions (FR-003 from spec.md).
    """
    email: EmailStr = PydField(description="User email address")
    password: str = PydField(min_length=8, description="Password (min 8 chars)")

    # Profile fields (required at signup)
    software_background: SoftwareBackground = PydField(
        description="Software development experience: Beginner, Intermediate, or Advanced"
    )
    hardware_background: HardwareBackground = PydField(
        description="Hardware/robotics experience: None, Basic, or Hands-on"
    )
    python_familiar: bool = PydField(
        default=False,
        description="Familiarity with Python programming"
    )
    ros_familiar: bool = PydField(
        default=False,
        description="Familiarity with ROS (Robot Operating System)"
    )
    aiml_familiar: bool = PydField(
        default=False,
        description="Familiarity with AI/ML concepts"
    )


# T018-T020: FastAPI-Users authentication setup

# Initialize FastAPI-Users with our User model and auth backend
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Current user dependency for protected endpoints
current_user = fastapi_users.current_user(active=True)

# Include authentication routers
# T018: Auth router (login, logout)
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Authentication"],
)

# T019: Registration router with custom UserCreate schema
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Authentication"],
)

# T020: Profile endpoint GET /auth/me
@router.get("/auth/me", response_model=UserRead, tags=["Authentication"])
async def get_current_user_profile(user: User = Depends(current_user)):
    """
    Get current logged-in user's profile.

    Returns user data including profile answers (software/hardware background, etc.).
    Requires valid authentication cookie.

    Response: UserRead with all profile fields
    """
    return UserRead.model_validate(user)


# ====================
# Phase 3: User Story 1 - Ask Question and Get Answer
# ====================

from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi import Depends
from sqlmodel import Session, select
from db.postgres import get_session, insert_chapters, insert_paragraphs
from db.qdrant_client import batch_upsert_with_retry, COLLECTION_OPENAI, COLLECTION_LOCAL
from rag.chunker import process_book
from rag.embedder import get_embedder
from agents.rag_agent import get_rag_agent
from models.session import Session as ChatSession
from models.chat import ChatHistory
import uuid
import time
import os


# Request/Response models for /admin/load_book
class LoadBookRequest(BaseModel):
    """Request schema for POST /admin/load_book"""
    book_path: str = Field(description="Path to book content file")
    chunk_size: Optional[int] = Field(default=512, description="Chunk size in tokens")
    overlap: Optional[int] = Field(default=50, description="Chunk overlap in tokens")
    embedding_model: Optional[str] = Field(default="openai", description="Embedding model: 'openai' or 'local'")


class LoadBookResponse(BaseModel):
    """Response schema for POST /admin/load_book"""
    status: str
    chunks_created: int
    qdrant_upserted: int
    chapters_processed: int
    processing_time_seconds: float
    embedding_model_used: str
    message: str


# Request/Response models for /chat
class ChatRequest(BaseModel):
    """Request schema for POST /chat"""
    session_id: Optional[str] = Field(default=None, description="Session ID (generated if not provided)")
    query: str = Field(max_length=2000, description="User question (max 2000 chars)")
    chapter_filter: Optional[int] = Field(default=None, description="Optional chapter number filter")


class ChatResponse(BaseModel):
    """Response schema for POST /chat"""
    answer: str
    citations: List[dict]
    query_id: str
    session_id: str
    processing_time_ms: int


@router.post("/admin/load_book", response_model=LoadBookResponse, tags=["Admin"])
async def load_book(
    request: LoadBookRequest,
    session: Session = Depends(get_session)
):
    """
    Load and process book content into knowledge base.

    Processes book markdown file, generates embeddings, and stores in PostgreSQL + Qdrant.
    """
    start_time = time.time()

    try:
        # Validate file exists
        if not os.path.exists(request.book_path):
            raise HTTPException(
                status_code=400,
                detail=f"Book file not found at path: {request.book_path}"
            )

        # Read book content
        with open(request.book_path, 'r', encoding='utf-8') as f:
            book_content = f.read()

        logger.info(f"Loaded book from {request.book_path} ({len(book_content)} chars)")

        # Process book into chapters and chunks
        chapters = process_book(book_content)

        logger.info(f"Processed {len(chapters)} chapters")

        # Prepare data for database insertion
        chapters_data = []
        all_chunks = []

        for chapter in chapters:
            chapters_data.append({
                "chapter_number": chapter["chapter_number"],
                "title": chapter["chapter_title"],
                "word_count": sum(chunk["token_count"] for chunk in chapter["chunks"]) * 0.75  # Approx words
            })
            all_chunks.extend(chapter["chunks"])

        # Insert chapters into PostgreSQL
        db_chapters = insert_chapters(chapters_data, session)

        # Create chapter_id lookup
        chapter_id_map = {ch.chapter_number: ch.id for ch in db_chapters}

        # Generate embeddings
        embedder = get_embedder()
        logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")

        chunk_texts = [chunk["content"] for chunk in all_chunks]
        embeddings = embedder.embed_batch(chunk_texts)

        # Prepare Qdrant points and PostgreSQL paragraphs
        qdrant_points = []
        paragraphs_data = []

        for chunk, embedding in zip(all_chunks, embeddings):
            point_id = str(uuid.uuid4())

            # Qdrant point
            qdrant_points.append({
                "id": point_id,
                "vector": embedding,
                "payload": {
                    "chunk_id": point_id,
                    "chapter_number": chunk["chapter_number"],
                    "chapter_title": chunk["chapter_title"],
                    "section_name": chunk.get("section_name", ""),
                    "paragraph_index": chunk["paragraph_index"],
                    "content": chunk["content"],
                    "token_count": chunk["token_count"],
                    "char_count": chunk["char_count"],
                }
            })

            # PostgreSQL paragraph
            paragraphs_data.append({
                "chapter_id": chapter_id_map[chunk["chapter_number"]],
                "paragraph_index": chunk["paragraph_index"],
                "content": chunk["content"],
                "embedding_id": point_id,
                "para_metadata": {
                    "section_name": chunk.get("section_name", ""),
                    "token_count": chunk["token_count"],
                    "char_count": chunk["char_count"],
                }
            })

        # Upsert to Qdrant
        collection_name = COLLECTION_OPENAI if request.embedding_model == "openai" else COLLECTION_LOCAL
        qdrant_count = batch_upsert_with_retry(collection_name, qdrant_points)

        # Insert paragraphs into PostgreSQL
        insert_paragraphs(paragraphs_data, session)

        processing_time = time.time() - start_time

        return LoadBookResponse(
            status="success",
            chunks_created=len(all_chunks),
            qdrant_upserted=qdrant_count,
            chapters_processed=len(chapters),
            processing_time_seconds=round(processing_time, 2),
            embedding_model_used=request.embedding_model,
            message="Book successfully loaded into knowledge base"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading book: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading book: {str(e)}")


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    session: Session = Depends(get_session)
):
    """
    Submit a question to the chatbot and receive a grounded answer.

    Processes query through RAG pipeline: embedding → retrieval → reranking → answer generation.
    """
    start_time = time.time()

    try:
        # Validate query
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty or whitespace-only"
            )

        if len(request.query) > 2000:
            raise HTTPException(
                status_code=400,
                detail=f"Query too long ({len(request.query)} chars). Maximum is 2000 characters."
            )

        # Get or create session
        if request.session_id:
            # Verify session exists
            existing_session = session.exec(
                select(ChatSession).where(ChatSession.session_id == request.session_id)
            ).first()

            if not existing_session:
                raise HTTPException(
                    status_code=404,
                    detail=f"Session ID '{request.session_id}' not found"
                )

            session_id = request.session_id
        else:
            # Create new session
            session_id = str(uuid.uuid4())
            new_session = ChatSession(session_id=session_id, state="active")
            session.add(new_session)
            session.commit()

        # Generate answer using RAG agent with OpenAI fallback
        agent = get_rag_agent()
        result = agent.generate_answer_with_fallback(
            query=request.query,
            session_id=session_id,
            chapter_filter=request.chapter_filter
        )

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Save to chat history
        query_id = str(uuid.uuid4())
        chat_history = ChatHistory(
            id=query_id,
            session_id=session_id,
            query=request.query,
            answer=result["answer"],
            citations=result["citations"],
            processing_time_ms=processing_time_ms,
            retrieval_score=result.get("retrieval_score", 0.0)
        )
        session.add(chat_history)
        session.commit()

        return ChatResponse(
            answer=result["answer"],
            citations=result["citations"],
            query_id=query_id,
            session_id=session_id,
            processing_time_ms=processing_time_ms
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


# ====================
# Phase 4: User Story 2 - Personalized Chapter Content (P2)
# ====================

from typing import Literal
from models.personalized_content import PersonalizedContent, DifficultyLevel
from models.book import Chapter, Paragraph
from agents.personalization_agent import get_personalization_agent
from api.dependencies import limiter
import time as time_module


class PersonalizationRequest(BaseModel):
    """
    Request schema for POST /personalize.

    User selects difficulty level for chapter content personalization.
    """
    chapter_id: int = Field(
        ge=1,
        le=8,
        description="Chapter ID (1-8 for the 8 book chapters)"
    )
    difficulty_level: Literal["Beginner", "Intermediate", "Advanced"] = Field(
        description="Target difficulty level for content adaptation"
    )


class PersonalizationResponse(BaseModel):
    """
    Response schema for POST /personalize.

    Returns personalized content with metadata about cache status and timing.
    """
    chapter_id: int
    difficulty_level: str
    personalized_content: str
    cached: bool = Field(description="True if content was retrieved from cache")
    processing_time_ms: int = Field(description="Time taken to process request in milliseconds")

    class Config:
        schema_extra = {
            "example": {
                "chapter_id": 3,
                "difficulty_level": "Beginner",
                "personalized_content": "# Chapter 3: Actuation Systems (Beginner)\n\nActuators are like the muscles of a robot...",
                "cached": True,
                "processing_time_ms": 342
            }
        }


@router.post("/personalize", response_model=PersonalizationResponse, tags=["Personalization"])
@limiter.limit("10/minute")  # Rate limiting: prevent abuse during demo
async def personalize_chapter(
    request: PersonalizationRequest,
    req: Request,  # Required for rate limiter
    user: User = Depends(current_user),  # Require authentication
    session: Session = Depends(get_session)
):
    """
    Personalize chapter content for user's selected difficulty level.

    Implements Hackathon Bonus Feature 2 (50 points):
    - Adapts chapter content to Beginner/Intermediate/Advanced levels
    - Uses OpenAI GPT-3.5-turbo for content transformation
    - Caches results for fast subsequent requests (<2s)
    - Fallback to original content if personalization fails

    Requirements:
    - User must be authenticated (logged in)
    - chapter_id must be valid (1-8)
    - difficulty_level must be Beginner/Intermediate/Advanced

    Performance:
    - Cache hit: <2s (SC-004)
    - Cache miss: <10s (includes OpenAI API call) (SC-003)

    Returns:
        PersonalizationResponse with personalized content and metadata

    Raises:
        401: If user not authenticated
        404: If chapter not found
        500: If personalization fails (returns original content as fallback)
    """
    start_time = time_module.time()

    try:
        # Step 1: Check cache first (PersonalizedContent table)
        logger.info(f"Personalization request: chapter_id={request.chapter_id}, level={request.difficulty_level}, user={user.email}")

        cached_content = session.exec(
            select(PersonalizedContent).where(
                PersonalizedContent.chapter_id == request.chapter_id,
                PersonalizedContent.difficulty_level == request.difficulty_level
            )
        ).first()

        if cached_content:
            # Cache hit - return immediately
            processing_time_ms = int((time_module.time() - start_time) * 1000)
            logger.info(f"Cache HIT for chapter {request.chapter_id} ({request.difficulty_level}) - {processing_time_ms}ms")

            return PersonalizationResponse(
                chapter_id=request.chapter_id,
                difficulty_level=request.difficulty_level,
                personalized_content=cached_content.personalized_text,
                cached=True,
                processing_time_ms=processing_time_ms
            )

        # Step 2: Cache miss - fetch original chapter content
        logger.info(f"Cache MISS for chapter {request.chapter_id} ({request.difficulty_level}) - generating personalized content")

        # Get chapter metadata
        chapter = session.exec(
            select(Chapter).where(Chapter.chapter_number == request.chapter_id)
        ).first()

        if not chapter:
            raise HTTPException(
                status_code=404,
                detail=f"Chapter {request.chapter_id} not found"
            )

        # Get all paragraphs for this chapter
        paragraphs = session.exec(
            select(Paragraph)
            .where(Paragraph.chapter_id == chapter.id)
            .order_by(Paragraph.paragraph_index)
        ).all()

        if not paragraphs:
            raise HTTPException(
                status_code=404,
                detail=f"No content found for chapter {request.chapter_id}"
            )

        # Assemble full chapter content
        original_content = f"# Chapter {request.chapter_id}: {chapter.title}\n\n"
        original_content += "\n\n".join([p.content for p in paragraphs])

        # Step 3: Call personalization agent
        try:
            personalization_agent = get_personalization_agent()
            personalized_text = await personalization_agent.personalize_content(
                content=original_content,
                difficulty_level=request.difficulty_level  # type: ignore
            )

            if not personalized_text:
                # Personalization failed - fallback to original content
                logger.warning(f"Personalization returned None for chapter {request.chapter_id} - using original content")
                personalized_text = original_content
                cached_flag = False
            else:
                # Step 4: Store in cache
                new_cached_content = PersonalizedContent(
                    chapter_id=request.chapter_id,
                    difficulty_level=request.difficulty_level,
                    personalized_text=personalized_text
                )
                session.add(new_cached_content)
                session.commit()
                logger.info(f"Cached personalized content for chapter {request.chapter_id} ({request.difficulty_level})")
                cached_flag = False

        except Exception as e:
            # Error during personalization - fallback to original content
            logger.error(f"Personalization failed for chapter {request.chapter_id}: {e}", exc_info=True)
            personalized_text = original_content
            cached_flag = False

        # Step 5: Return response
        processing_time_ms = int((time_module.time() - start_time) * 1000)
        logger.info(f"Personalization complete for chapter {request.chapter_id} - {processing_time_ms}ms")

        return PersonalizationResponse(
            chapter_id=request.chapter_id,
            difficulty_level=request.difficulty_level,
            personalized_content=personalized_text,
            cached=cached_flag,
            processing_time_ms=processing_time_ms
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in personalization endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Personalization service error: {str(e)}"
        )


# ====================
# Phase 5: User Story 3 - Urdu Translation (P3)
# ====================

from models.translation import Translation
from agents.translation_agent import get_translation_agent


class TranslationRequest(BaseModel):
    """
    Request schema for POST /translate.

    User requests translation of chapter content to Urdu.
    """
    chapter_id: int = Field(
        ge=1,
        le=8,
        description="Chapter ID (1-8 for the 8 book chapters)"
    )
    target_lang: str = Field(
        default="ur",
        description="Target language code (default: 'ur' for Urdu)"
    )


class TranslationResponse(BaseModel):
    """
    Response schema for POST /translate.

    Returns both original and translated content with metadata.
    """
    chapter_id: int
    language_code: str
    original_text: str
    translated_text: str
    cached: bool = Field(description="True if translation was retrieved from cache")
    processing_time_ms: int = Field(description="Time taken to process request in milliseconds")

    class Config:
        schema_extra = {
            "example": {
                "chapter_id": 3,
                "language_code": "ur",
                "original_text": "# Chapter 3: Actuation Systems\n\nActuation systems are...",
                "translated_text": "# باب 3: Actuation Systems\n\nActuation systems یہ ہیں...",
                "cached": True,
                "processing_time_ms": 1250
            }
        }


@router.post("/translate", response_model=TranslationResponse, tags=["Translation"])
@limiter.limit("10/minute")  # Rate limiting: prevent abuse
async def translate_chapter(
    request: TranslationRequest,
    req: Request,  # Required for rate limiter
    session: Session = Depends(get_session)
):
    """
    Translate chapter content to Urdu.

    Implements Hackathon Bonus Feature 3 (25 points):
    - Translates chapter content from English to Urdu
    - Preserves technical terms in English for clarity
    - Caches translations for fast subsequent requests (<2s)
    - Returns both original and translated text for side-by-side display

    Requirements:
    - chapter_id must be valid (1-8)
    - No authentication required (accessible to all users)

    Performance:
    - Cache hit: <2s (SC-004)
    - Cache miss: <15s (includes OpenAI API call) (SC-005)

    Returns:
        TranslationResponse with original and translated content

    Raises:
        404: If chapter not found
        500: If translation fails (English content still accessible)
    """
    start_time = time_module.time()

    try:
        # Step 1: Check cache first (Translation table)
        logger.info(f"Translation request: chapter_id={request.chapter_id}, lang={request.target_lang}")

        cached_translation = session.exec(
            select(Translation).where(
                Translation.chapter_id == request.chapter_id,
                Translation.language_code == request.target_lang
            )
        ).first()

        # Get chapter content (needed for both cache hit and miss)
        chapter = session.exec(
            select(Chapter).where(Chapter.chapter_number == request.chapter_id)
        ).first()

        if not chapter:
            raise HTTPException(
                status_code=404,
                detail=f"Chapter {request.chapter_id} not found"
            )

        # Get all paragraphs for this chapter
        paragraphs = session.exec(
            select(Paragraph)
            .where(Paragraph.chapter_id == chapter.id)
            .order_by(Paragraph.paragraph_index)
        ).all()

        if not paragraphs:
            raise HTTPException(
                status_code=404,
                detail=f"No content found for chapter {request.chapter_id}"
            )

        # Assemble full chapter content
        original_content = f"# Chapter {request.chapter_id}: {chapter.title}\n\n"
        original_content += "\n\n".join([p.content for p in paragraphs])

        if cached_translation:
            # Cache hit - return immediately
            processing_time_ms = int((time_module.time() - start_time) * 1000)
            logger.info(f"Cache HIT for chapter {request.chapter_id} ({request.target_lang}) - {processing_time_ms}ms")

            return TranslationResponse(
                chapter_id=request.chapter_id,
                language_code=request.target_lang,
                original_text=original_content,
                translated_text=cached_translation.translated_text,
                cached=True,
                processing_time_ms=processing_time_ms
            )

        # Step 2: Cache miss - translate content
        logger.info(f"Cache MISS for chapter {request.chapter_id} ({request.target_lang}) - translating content")

        try:
            translation_agent = get_translation_agent()
            translated_text = await translation_agent.translate_to_urdu(
                content=original_content
            )

            if not translated_text:
                # Translation failed - return original content with error flag
                logger.warning(f"Translation returned None for chapter {request.chapter_id} - English content still accessible")
                processing_time_ms = int((time_module.time() - start_time) * 1000)

                return TranslationResponse(
                    chapter_id=request.chapter_id,
                    language_code=request.target_lang,
                    original_text=original_content,
                    translated_text=original_content,  # Fallback to original
                    cached=False,
                    processing_time_ms=processing_time_ms
                )

            # Step 3: Store in cache
            new_translation = Translation(
                chapter_id=request.chapter_id,
                language_code=request.target_lang,
                original_text=original_content,
                translated_text=translated_text
            )
            session.add(new_translation)
            session.commit()
            logger.info(f"Cached translation for chapter {request.chapter_id} ({request.target_lang})")

            processing_time_ms = int((time_module.time() - start_time) * 1000)
            logger.info(f"Translation complete for chapter {request.chapter_id} - {processing_time_ms}ms")

            return TranslationResponse(
                chapter_id=request.chapter_id,
                language_code=request.target_lang,
                original_text=original_content,
                translated_text=translated_text,
                cached=False,
                processing_time_ms=processing_time_ms
            )

        except Exception as e:
            # Error during translation - return original content (FR-026)
            logger.error(f"Translation failed for chapter {request.chapter_id}: {e}", exc_info=True)
            processing_time_ms = int((time_module.time() - start_time) * 1000)

            return TranslationResponse(
                chapter_id=request.chapter_id,
                language_code=request.target_lang,
                original_text=original_content,
                translated_text=original_content,  # Fallback to original
                cached=False,
                processing_time_ms=processing_time_ms
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in translation endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Translation service error: {str(e)}"
        )


# Future endpoints (Phase 4 - User Story 2):
# - GET /history/{session_id}
#
# Future endpoints (Phase 6 - User Story 4):
# - DELETE /history/{session_id}
#
# Future endpoints (Phase 8 - Polish):
# - GET /ready
