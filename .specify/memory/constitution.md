<!--
Sync Impact Report:
Version change: 1.0.0 (old) → 2.0.0 (new)
Modified principles:
  - I. Fast Loading & Performance → I. Grounded Retrieval (RAG-First Architecture)
  - II. Clean & Modern Aesthetics → II. Performance & Cost Efficiency
  - III. Robotics-Themed Interface → III. Data Integrity & Schema Consistency
  - IV. Responsive Design → IV. Security & Input Validation
  - V. Component-Based Structure → V. Clean Architecture & Minimal Dependencies
Added sections:
  - VI. Observability & Production Readiness
  - VII. Personalization & User Experience
  - VIII. Multilingual Support (Urdu Translation)
  - IX. Hallucination Prevention & Guardrails
  - X. Testing & Quality Assurance
  - Technology Stack section
  - System Architecture section
  - Data Flow section
Removed sections: Robotics UI-focused content replaced with RAG system principles
Templates requiring updates:
  - .specify/templates/plan-template.md ⚠ pending
  - .specify/templates/spec-template.md ⚠ pending
  - .specify/templates/tasks-template.md ⚠ pending
Follow-up TODOs: Validate template alignment with new RAG-focused principles
-->
# RAG Chatbot Constitution: Physical AI & Humanoid Robotics Essentials

**Project Name**: RAG Chatbot for "Physical AI & Humanoid Robotics Essentials"
**Version**: 2.0.0
**Ratified**: 2025-12-12
**Last Amended**: 2025-12-12

## Executive Summary

This constitution defines the foundational principles, architectural constraints, and governance model for a production-grade Retrieval-Augmented Generation (RAG) chatbot system. The system serves as an intelligent interface to the book "Physical AI & Humanoid Robotics Essentials," providing grounded, citation-backed answers, personalized learning experiences, and multilingual support.

## Technology Stack

**Backend Framework**: FastAPI (Python 3.11+)
**Database ORM**: SQLModel
**Primary Database**: Neon PostgreSQL
**Vector Database**: Qdrant (local dev / cloud production)
**AI Runtime**: OpenAI Agents SDK
**Embeddings**: text-embedding-3-small (primary) / sentence-transformers/all-MiniLM-L6-v2 (fallback)
**Reranker**: sentence-transformers/all-MiniLM-L6-v2 (local) / OpenAI reranker API (cloud)
**LLM Provider**: OpenAI (GPT-4 or GPT-3.5-turbo)

## System Architecture

```
┌─────────────┐
│   FastAPI   │ ← User Query
│   Backend   │
└──────┬──────┘
       │
       ├──→ [Neon PostgreSQL] ← User profiles, chat history, quizzes, summaries
       │
       ├──→ [Qdrant Vector DB] ← Book chunks + embeddings + metadata
       │
       └──→ [OpenAI Agents SDK] ← Answer generation with grounding
```

## Data Flow

1. **Ingestion**: Book → Chunking → Embeddings → Qdrant upsert + PostgreSQL metadata
2. **Retrieval**: User query → Embedding → Qdrant search (top_k) → Reranking → Context
3. **Generation**: Context + query → OpenAI Agent → Grounded answer + citations
4. **Storage**: Answer + citations → PostgreSQL chat history

## Core Principles

### I. Grounded Retrieval (RAG-First Architecture)

**Principle**: Every answer MUST be grounded in the source book content. The system SHALL NOT generate responses from pre-trained knowledge alone.

**Requirements**:
- All chatbot responses MUST include citations (chapter, paragraph/section references)
- Retrieval pipeline MUST return source metadata alongside chunks
- Answers without retrievable context MUST trigger a fallback: "I cannot answer this from the book content."
- System prompt MUST explicitly instruct the LLM to only use provided context
- Citation format: `{"chapter": "Chapter X", "paragraph": "Section Y.Z"}`

**Rationale**: Prevents hallucination and maintains fidelity to the authoritative source material, ensuring users receive accurate, verifiable information.

### II. Performance & Cost Efficiency

**Principle**: The system MUST prioritize fast response times and minimal operational costs while maintaining quality.

**Requirements**:
- Query latency target: p95 < 2 seconds (embedding + retrieval + generation)
- Embedding model: Use text-embedding-3-small (1536 dims) for cost/performance balance
- Local fallback: sentence-transformers/all-MiniLM-L6-v2 (384 dims) for dev/offline
- Batch processing: Book ingestion and embeddings MUST support batch operations
- Caching: Frequently asked questions and translations MUST be cached in PostgreSQL
- LLM selection: Use GPT-3.5-turbo for simple queries; GPT-4 for complex reasoning (configurable)
- Resource limits: API calls MUST respect rate limits; implement exponential backoff

**Rationale**: Ensures scalability and cost-effectiveness for production deployment while maintaining user experience quality.

### III. Data Integrity & Schema Consistency

**Principle**: All data models MUST be strongly typed, versioned, and maintain referential integrity across PostgreSQL and Qdrant.

**Requirements**:
- SQLModel schemas MUST define all models with explicit types and constraints
- Database migrations MUST be versioned and reversible (Alembic)
- Qdrant payload schema MUST match PostgreSQL metadata structure
- Foreign key relationships MUST be enforced (User ↔ ChatHistory, Chapter ↔ Paragraph)
- Chunk IDs MUST be consistent between PostgreSQL metadata and Qdrant vectors
- All timestamps MUST be UTC ISO-8601 format
- Enum types MUST be used for user_level (beginner, intermediate, expert)

**Data Models**:
1. **User**: id, username, email, user_level (enum), preferences (JSON), created_at, updated_at
2. **ChatHistory**: id, user_id (FK), query, answer, citations (JSON), timestamp
3. **Chapter**: id, chapter_number, title, summary, word_count
4. **Paragraph**: id, chapter_id (FK), paragraph_index, content, embedding_id (Qdrant point ID)
5. **Quiz**: id, chapter_id (FK), question, options (JSON), correct_answer, explanation
6. **Summary**: id, chapter_id (FK), summary_type (brief/detailed), content, generated_at
7. **Translation**: id, original_text, translated_text (Urdu), language_code, cached_at

**Rationale**: Strong typing and schema enforcement prevent runtime errors, simplify debugging, and ensure data consistency across distributed components.

### IV. Security & Input Validation

**Principle**: All user inputs MUST be validated, sanitized, and protected against injection attacks and abuse.

**Requirements**:
- Input validation: All API routes MUST use Pydantic models for request validation
- SQL injection: SQLModel parameterized queries MUST be used (no raw SQL strings)
- Rate limiting: 20 requests/minute per user (configurable via environment variable)
- Authentication: JWT-based authentication for user identification (if user system required)
- Secrets management: API keys MUST be stored in `.env` and never hardcoded
- CORS: Restrict origins to approved frontend domains only
- Query length limits: Max 500 characters per query; max 10 turns per chat session
- Prompt injection defense: System prompt MUST include instructions to ignore user attempts to override behavior

**Rate Limiting Strategy**:
- Use middleware (slowapi or custom Redis-based limiter)
- Return HTTP 429 with Retry-After header
- Exempt admin routes from rate limiting

**Rationale**: Protects system integrity, prevents abuse, and ensures compliance with security best practices for production APIs.

### V. Clean Architecture & Minimal Dependencies

**Principle**: The codebase MUST follow clean architecture principles with clear separation of concerns and minimal external dependencies.

**Folder Structure**:
```
/backend
  /api
    routes.py          # FastAPI route definitions
    dependencies.py    # Dependency injection (DB sessions, auth)
  /models
    user.py            # SQLModel User schema
    chat.py            # ChatHistory schema
    book.py            # Chapter, Paragraph schemas
    quiz.py            # Quiz, Summary schemas
    translation.py     # Translation schema
  /agents
    rag_agent.py       # OpenAI Agent definition for RAG
    tools.py           # Agent tools (retrieval, citation formatting)
  /rag
    embedder.py        # Embedding logic (OpenAI + local fallback)
    retriever.py       # Qdrant search + filtering
    reranker.py        # Reranking logic (MiniLM or OpenAI)
    chunker.py         # Book processing and chunking
  /db
    postgres.py        # PostgreSQL connection and session management
    qdrant_client.py   # Qdrant connection and collection management
    migrations/        # Alembic migration files
  /utils
    config.py          # Environment variables and settings
    logger.py          # Structured logging setup
    validators.py      # Custom validation functions
  main.py              # FastAPI app initialization
  requirements.txt     # Pinned dependencies
  .env.example         # Example environment variables
```

**Dependencies (Core Only)**:
- fastapi, uvicorn (web server)
- sqlmodel, psycopg2-binary (PostgreSQL ORM)
- qdrant-client (vector DB)
- openai (LLM + embeddings)
- sentence-transformers (local embeddings/reranking)
- pydantic (validation)
- python-dotenv (config)
- slowapi (rate limiting)

**Requirements**:
- Each module MUST have a single, well-defined responsibility
- Cross-cutting concerns (logging, auth) MUST use dependency injection
- Business logic MUST NOT directly import FastAPI request objects
- All external API calls MUST be wrapped in client classes with error handling
- No circular imports allowed

**Rationale**: Clean architecture improves maintainability, testability, and onboarding speed. Minimal dependencies reduce security surface area and dependency conflicts.

### VI. Observability & Production Readiness

**Principle**: The system MUST provide comprehensive observability for debugging, monitoring, and performance analysis.

**Requirements**:
- **Logging**: Structured JSON logs with correlation IDs for tracing requests across services
- **Metrics**: Track latency (p50, p95, p99), error rates, cache hit rates, cost per query
- **Health checks**: `/health` and `/ready` endpoints for container orchestration
- **Error handling**: All exceptions MUST be caught, logged, and return standardized error responses
- **Graceful degradation**: If Qdrant is unavailable, return cached answers or degraded service message
- **Alerting**: Monitor for high error rates, slow queries (>5s), API quota exhaustion
- **Deployment**: Support Docker containerization with multi-stage builds for production

**Error Response Schema**:
```json
{
  "error": "error_code",
  "message": "Human-readable message",
  "details": {},
  "request_id": "uuid"
}
```

**Rationale**: Production systems require visibility into failures and performance bottlenecks to ensure reliability and fast incident response.

### VII. Personalization & User Experience

**Principle**: The system MUST adapt responses to user expertise levels and learning goals.

**Requirements**:
- User profiles MUST capture `user_level` (beginner, intermediate, expert)
- System prompts MUST include user level in context:
  - **Beginner**: Simplified language, more explanations, avoid jargon
  - **Intermediate**: Balanced technical detail, some assumptions
  - **Expert**: Dense technical language, advanced concepts, concise answers
- API route: `POST /users/profile` to set/update user preferences
- Personalization flow:
  1. Retrieve user profile from PostgreSQL
  2. Inject user_level into system prompt
  3. Adjust retrieval strategy (e.g., beginners get more foundational chapters)
- Chat history MUST be retrievable per user: `GET /history/{user_id}`

**Rationale**: Personalization improves learning outcomes and user satisfaction by matching content complexity to user expertise.

### VIII. Multilingual Support (Urdu Translation)

**Principle**: The system MUST support Urdu translation for answers to broaden accessibility.

**Requirements**:
- API route: `POST /translate` accepts `{"text": "...", "target_lang": "ur"}`
- Translation caching: Store original + translated text in `Translation` table
- Cache key: hash(original_text + target_lang)
- Before calling OpenAI translation API, check cache (TTL: 30 days)
- Integration: After answer generation, optionally translate before returning to user
- Prompt template for translation:
  ```
  Translate the following technical text about Physical AI and Robotics into Urdu.
  Preserve technical terms where appropriate. Ensure clarity for non-English speakers.

  Text: {original_text}
  ```

**Rationale**: Increases accessibility for Urdu-speaking learners and expands the system's reach to non-English audiences.

### IX. Hallucination Prevention & Guardrails

**Principle**: The system MUST implement multiple layers of guardrails to prevent hallucinated or off-topic responses.

**Requirements**:
- **System prompt guardrails**:
  - "You MUST only answer questions using the provided book excerpts."
  - "If the answer is not in the context, respond: 'This information is not covered in the provided book content.'"
  - "Never use your pre-trained knowledge to answer questions about the book."
- **Retrieval validation**: If top retrieval score < 0.7 (cosine similarity), trigger low-confidence warning
- **Citation enforcement**: Answers without citations MUST be rejected (post-processing validation)
- **Content filtering**: Detect and block attempts to jailbreak the system prompt (e.g., "ignore previous instructions")
- **Grounding check**: Use a lightweight classifier to verify answer semantic similarity to retrieved chunks

**Rationale**: Hallucination undermines trust in the system. Layered guardrails ensure answers remain faithful to source material.

### X. Testing & Quality Assurance

**Principle**: All code MUST be tested with unit, integration, and end-to-end tests before deployment.

**Requirements**:
- **Unit tests**: 80%+ coverage for business logic (RAG pipeline, chunking, reranking)
- **Integration tests**: Test API routes with mock DB and Qdrant
- **End-to-end tests**: Full pipeline tests (query → retrieval → answer) with sample book data
- **Fixtures**: Use pytest fixtures for DB sessions, Qdrant collections, sample embeddings
- **CI/CD**: Run tests on every commit (GitHub Actions or equivalent)
- **Load testing**: Simulate 100 concurrent users to validate performance targets

**Test Categories**:
1. **Retrieval accuracy**: Test top-k recall for known question-answer pairs
2. **Citation correctness**: Verify citations match source chunks
3. **Personalization**: Test answer variation across user levels
4. **Translation**: Validate Urdu output quality (manual spot checks)
5. **Security**: Test rate limiting, input validation, SQL injection attempts

**Rationale**: Comprehensive testing prevents regressions, ensures reliability, and validates system behavior under load.

## Book Processing Pipeline

### Chunking Strategy

**Chunk Size**: 512 tokens (target), max 600 tokens
**Chunk Overlap**: 50 tokens
**Splitting Logic**: Sentence-boundary splitting (avoid mid-sentence cuts)
**Cleaning Rules**:
- Remove page numbers, headers, footers
- Normalize whitespace (replace multiple spaces/newlines with single space)
- Preserve formatting for code blocks (if any)
- Strip special characters (except punctuation)

**Metadata Schema** (per chunk):
```python
{
  "chunk_id": "uuid",
  "chapter_number": int,
  "chapter_title": str,
  "paragraph_index": int,
  "section_name": str (optional),
  "char_count": int,
  "token_count": int,
  "source_page": int (if available)
}
```

### Qdrant Vector Store Schema

**Collection Name**: `physical_ai_robotics_book`
**Vector Size**: 1536 (text-embedding-3-small) OR 384 (MiniLM fallback)
**Distance Metric**: Cosine
**HNSW Config**:
- `m`: 16 (number of edges per node)
- `ef_construct`: 100 (construction time accuracy)

**Payload Structure**:
```json
{
  "chunk_id": "uuid",
  "chapter_number": 3,
  "chapter_title": "Actuation Systems",
  "paragraph_index": 5,
  "content": "Hydraulic actuators provide high force density...",
  "section_name": "3.2 Hydraulic vs. Electric Actuators",
  "token_count": 487
}
```

**Filtering Fields**: `chapter_number`, `section_name`

**Upsert Strategy**: Batch upsert (100 points per batch) with retry on failure

## Retrieval Pipeline

**Process**:
1. **Query Embedding**: Embed user query using text-embedding-3-small
2. **Qdrant Search**: Search top_k=10 chunks (cosine similarity)
3. **Optional Filtering**: If user requests specific chapter, filter by `chapter_number`
4. **Reranking**: Rerank top 10 → top 5 using cross-encoder (MiniLM)
5. **Citation Mapping**: Extract chapter + paragraph metadata from top 5
6. **Context Assembly**: Concatenate top 5 chunks with metadata for LLM

**FastAPI Function Signature**:
```python
async def retrieve_context(
    query: str,
    top_k: int = 10,
    rerank_top_n: int = 5,
    chapter_filter: Optional[int] = None
) -> List[RetrievalResult]:
    ...
```

## Answer Generation (OpenAI Agents SDK)

**System Prompt**:
```
You are an expert assistant for the book "Physical AI & Humanoid Robotics Essentials."
Your role is to answer questions ONLY using the provided book excerpts.

Rules:
1. Answer ONLY from the provided context.
2. If the answer is not in the context, respond: "This information is not covered in the provided book content."
3. Always include citations in your response (chapter and section).
4. Adapt your language to the user's expertise level: {user_level}.
5. Be concise but thorough.
```

**Input Schema**:
```python
class RAGQueryInput(BaseModel):
    query: str
    context: List[str]  # Retrieved chunks
    citations: List[Dict[str, Any]]  # Metadata for citations
    user_level: UserLevel  # Enum: beginner, intermediate, expert
```

**Output Schema**:
```python
class RAGAnswerOutput(BaseModel):
    answer: str
    citations: List[Citation]

class Citation(BaseModel):
    chapter: str
    paragraph: str
```

## API Routes

### 1. POST /chat
**Description**: Main chatbot endpoint
**Request**:
```json
{
  "user_id": "uuid",
  "query": "What are hydraulic actuators?",
  "chapter_filter": null
}
```
**Response**:
```json
{
  "answer": "Hydraulic actuators are...",
  "citations": [
    {"chapter": "Chapter 3", "paragraph": "Section 3.2"}
  ],
  "query_id": "uuid"
}
```

### 2. GET /history/{user_id}
**Description**: Retrieve chat history for a user
**Response**:
```json
{
  "user_id": "uuid",
  "history": [
    {
      "query": "...",
      "answer": "...",
      "citations": [...],
      "timestamp": "2025-12-12T10:30:00Z"
    }
  ]
}
```

### 3. POST /embed/load_book
**Description**: Admin route to process and embed book content
**Request**:
```json
{
  "book_path": "/path/to/book.txt",
  "chunk_size": 512,
  "overlap": 50
}
```
**Response**:
```json
{
  "status": "success",
  "chunks_created": 1523,
  "qdrant_upserted": 1523
}
```

### 4. POST /summaries/generate
**Description**: Generate chapter summaries
**Request**:
```json
{
  "chapter_id": "uuid",
  "summary_type": "brief"
}
```
**Response**:
```json
{
  "summary_id": "uuid",
  "content": "This chapter covers..."
}
```

### 5. POST /quizzes/generate
**Description**: Generate quiz questions for a chapter
**Request**:
```json
{
  "chapter_id": "uuid",
  "num_questions": 5
}
```
**Response**:
```json
{
  "quizzes": [
    {
      "question": "What is...",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "B",
      "explanation": "..."
    }
  ]
}
```

### 6. POST /translate
**Description**: Translate text to Urdu
**Request**:
```json
{
  "text": "Hydraulic actuators provide...",
  "target_lang": "ur"
}
```
**Response**:
```json
{
  "original": "Hydraulic actuators provide...",
  "translated": "ہائیڈرولک ایکچوایٹرز...",
  "cached": false
}
```

## Governance

### Amendment Process

1. **Proposal**: Submit proposed changes via pull request to `.specify/memory/constitution.md`
2. **Review**: Technical lead reviews for consistency with project goals and technical feasibility
3. **Approval**: Requires approval from project maintainer(s)
4. **Version Bump**: Increment version according to semantic versioning rules
5. **Propagation**: Update dependent templates and documentation

### Versioning Policy

- **MAJOR**: Backward-incompatible changes to data models, APIs, or core principles
- **MINOR**: New principles, features, or significant expansions to existing guidance
- **PATCH**: Clarifications, typo fixes, non-semantic refinements

### Compliance Review

- All feature specifications MUST reference relevant constitutional principles
- All pull requests MUST include a constitutional compliance checklist
- Quarterly audits to verify adherence to principles (automated where possible)

### Conflict Resolution

If principles conflict during implementation:
1. Prioritize security and data integrity over performance
2. Prioritize grounding and hallucination prevention over response variety
3. Escalate to technical lead for architectural decisions

## Acceptance Criteria

Before marking any development task complete:
- [ ] All code changes align with constitutional principles
- [ ] Unit tests written and passing (80%+ coverage)
- [ ] API routes include input validation and error handling
- [ ] Database migrations tested (up and down)
- [ ] Performance targets validated (p95 < 2s)
- [ ] Security checklist completed (rate limiting, input validation)
- [ ] Hallucination guardrails tested with adversarial queries
- [ ] Documentation updated (API docs, README)

## References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- Qdrant Documentation: https://qdrant.tech/documentation/
- OpenAI Agents SDK: https://github.com/openai/openai-agents-sdk
- Sentence Transformers: https://www.sbert.net/

---

*This constitution is a living document. Amendments must preserve the core mission: delivering grounded, accurate, personalized answers from "Physical AI & Humanoid Robotics Essentials."*
