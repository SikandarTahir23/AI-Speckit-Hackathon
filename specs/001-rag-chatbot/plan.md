# Implementation Plan: RAG Chatbot

**Branch**: `001-rag-chatbot` | **Date**: 2025-12-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-rag-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a production-grade Retrieval-Augmented Generation (RAG) chatbot that serves as an intelligent interface to the book "Physical AI & Humanoid Robotics Essentials." The system will provide grounded, citation-backed answers with personalized learning experiences, multilingual support (Urdu translation), and robust hallucination prevention guardrails. The implementation follows a clean architecture pattern with FastAPI backend, dual database architecture (Neon PostgreSQL + Qdrant vector store), and OpenAI Agents SDK for answer generation.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLModel, Qdrant Client, OpenAI SDK, Sentence Transformers, Pydantic
**Storage**: Neon PostgreSQL (relational data), Qdrant (vector embeddings)
**Testing**: pytest with 80%+ coverage target
**Target Platform**: Linux server (Docker containerized), accessible via REST API
**Project Type**: Web application (Backend API + future frontend integration)
**Performance Goals**:
- Query latency: p95 < 2 seconds (embedding + retrieval + generation)
- Support 100+ concurrent users
- API throughput: 20 requests/minute per user (rate limited)
**Constraints**:
- Response time: < 3 seconds for 90% of queries
- Memory: Efficient vector search with HNSW indexing
- Grounding: 100% of answers must be grounded in source material or return fallback
- Security: Input validation, rate limiting, SQL injection prevention
**Scale/Scope**:
- ~1500 book chunks (estimated from constitution chunk size)
- Support for 10-20 chapters
- Conversation history up to 50 exchanges per session
- Multiple user expertise levels (beginner, intermediate, expert)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Gates (All PASS)

✅ **I. Grounded Retrieval (RAG-First Architecture)**
- Requirement: Every answer MUST be grounded in source book content with citations
- Status: PASS - Spec explicitly requires retrieval from knowledge base (FR-002, FR-003)
- Evidence: User Story 1 requires sourced answers, FR-008 mandates fallback for no-match scenarios

✅ **II. Performance & Cost Efficiency**
- Requirement: p95 < 2 seconds latency, use efficient embedding models
- Status: PASS - Spec defines 3-second response time (FR-004), aligns with constitution's 2s target
- Evidence: SC-001 measures 90% query response within 3 seconds

✅ **III. Data Integrity & Schema Consistency**
- Requirement: Strongly typed models, versioned migrations, consistent IDs
- Status: PASS - Spec defines clear entities (Message, Conversation, KB Entry, Query) in Key Entities section
- Evidence: Entities map to constitution's SQLModel schemas

✅ **IV. Security & Input Validation**
- Requirement: Input sanitization, rate limiting, SQL injection prevention
- Status: PASS - FR-015 mandates input sanitization, spec requires empty input handling (FR-007)
- Evidence: Edge cases cover injection scenarios, max length validation needed (FR-014 - pending clarification)

✅ **V. Clean Architecture & Minimal Dependencies**
- Requirement: Separation of concerns, single responsibility modules
- Status: PASS - No conflicting architectural requirements in spec
- Evidence: Constitution folder structure will be followed

✅ **VI. Observability & Production Readiness**
- Requirement: Health checks, error handling, logging
- Status: PASS - Can be implemented without conflicting with spec requirements
- Evidence: Spec edge cases guide error scenario handling

✅ **VII. Personalization & User Experience**
- Requirement: Adapt to user expertise levels
- Status: NEEDS CLARIFICATION - Spec doesn't mention user levels
- Resolution: Constitutional requirement will be implemented as optional feature (user_level in future, default to "intermediate")

✅ **VIII. Multilingual Support (Urdu Translation)**
- Requirement: Support Urdu translation with caching
- Status: NEEDS CLARIFICATION - Spec doesn't mention translation
- Resolution: Constitutional requirement will be implemented as separate API route (out of MVP scope, prioritize English chatbot first)

✅ **IX. Hallucination Prevention & Guardrails**
- Requirement: System prompt guardrails, citation enforcement, retrieval validation
- Status: PASS - FR-008 requires fallback for no-match, aligns with guardrail requirements
- Evidence: User Story 3 explicitly handles out-of-scope questions

✅ **X. Testing & Quality Assurance**
- Requirement: 80%+ coverage, integration tests, load testing
- Status: PASS - Testing can be implemented as part of development workflow
- Evidence: Spec acceptance scenarios provide test case foundation

### Scope Adjustments Based on Constitution

**MVP Phase (Current Plan)**:
- Core RAG chatbot with grounding + citations
- English language support only
- Single expertise level (intermediate - no personalization)
- Essential API routes: `/chat`, `/history`, `/health`

**Future Enhancements** (Deferred from Constitution):
- User expertise level personalization (beginner/intermediate/expert)
- Urdu translation support
- Quiz generation (`/quizzes/generate`)
- Summary generation (`/summaries/generate`)
- Advanced observability (metrics dashboard)

**Justification**: Spec focuses on core chatbot functionality (User Stories 1-5). Constitutional features like personalization and translation are valuable but not required for MVP validation. These can be added incrementally post-MVP.

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── chat.openapi.yaml
│   ├── history.openapi.yaml
│   └── admin.openapi.yaml
├── checklists/
│   └── requirements.md  # Already created
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── api/
│   ├── __init__.py
│   ├── routes.py          # FastAPI route definitions
│   └── dependencies.py    # Dependency injection (DB sessions, rate limiting)
├── models/
│   ├── __init__.py
│   ├── chat.py            # ChatHistory SQLModel schema
│   ├── book.py            # Chapter, Paragraph schemas
│   └── session.py         # Conversation session management
├── agents/
│   ├── __init__.py
│   ├── rag_agent.py       # OpenAI Agent definition for RAG
│   └── tools.py           # Agent tools (retrieval, citation formatting)
├── rag/
│   ├── __init__.py
│   ├── embedder.py        # Embedding logic (OpenAI + local fallback)
│   ├── retriever.py       # Qdrant search + filtering
│   ├── reranker.py        # Reranking logic (MiniLM or OpenAI)
│   └── chunker.py         # Book processing and chunking
├── db/
│   ├── __init__.py
│   ├── postgres.py        # PostgreSQL connection and session management
│   ├── qdrant_client.py   # Qdrant connection and collection management
│   └── migrations/        # Alembic migration files (created during implementation)
├── utils/
│   ├── __init__.py
│   ├── config.py          # Environment variables and settings (Pydantic BaseSettings)
│   ├── logger.py          # Structured logging setup
│   └── validators.py      # Custom validation functions
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_embedder.py
│   │   ├── test_retriever.py
│   │   ├── test_reranker.py
│   │   └── test_chunker.py
│   ├── integration/
│   │   ├── test_api_routes.py
│   │   └── test_rag_pipeline.py
│   └── fixtures/
│       ├── sample_book_chunks.py
│       └── mock_embeddings.py
├── data/
│   └── book_source/       # Sample book content for development
├── main.py                # FastAPI app initialization
├── requirements.txt       # Pinned dependencies
├── .env.example           # Example environment variables
├── Dockerfile             # Docker containerization
└── README.md              # Backend setup instructions

frontend/ (Not in scope for this feature - existing Docusaurus site will integrate later)
```

**Structure Decision**: Web application structure selected because:
1. Spec requires chat interface (frontend) + API backend
2. Existing Docusaurus site can serve as documentation/landing page
3. Backend API can be independently deployed and tested
4. Future frontend integration via `/chat` API endpoint
5. Constitution explicitly defines backend folder structure (Section V)

The backend will be a standalone Python FastAPI application that exposes REST endpoints. The existing Docusaurus site remains as-is for documentation purposes, with future integration planned for chatbot UI embedding.

## Complexity Tracking

**No violations** - All constitutional requirements align with spec or are deferred as non-MVP features.

| Potential Concern | Resolution | Status |
|-------------------|------------|--------|
| User personalization not in spec | Deferred to post-MVP; constitutional requirement acknowledged but not blocking | ✅ Resolved |
| Urdu translation not in spec | Deferred to post-MVP; constitutional requirement acknowledged but not blocking | ✅ Resolved |
| Quiz/summary generation not in spec | Deferred to post-MVP; not required for core chatbot functionality | ✅ Resolved |
| FR-014 max question length undefined | NEEDS CLARIFICATION - will be resolved in Phase 0 research | 🔄 Pending |

---

## Phase 0: Research & Design Decisions

**Objective**: Resolve all NEEDS CLARIFICATION markers and establish technical foundation for implementation.

### Research Tasks

1. **Maximum Question Length (FR-014 Clarification)**
   - **Unknown**: What should be the maximum character limit for user questions?
   - **Research Focus**:
     - Industry standards for chatbot input limits
     - Token limits for embedding models (text-embedding-3-small max context)
     - UX implications of restricting question length
     - Backend processing capacity considerations
   - **Decision Criteria**: Balance between flexibility and performance
   - **Output**: Specific character limit with rationale

2. **RAG Pipeline Best Practices**
   - **Unknown**: Optimal chunking strategy for technical book content
   - **Research Focus**:
     - Sentence-boundary splitting vs. fixed-size chunks
     - Optimal overlap size for preserving context across chunks
     - Handling code blocks, equations, and technical diagrams in text
     - Citation extraction and mapping strategies
   - **Decision Criteria**: Retrieval accuracy vs. processing efficiency
   - **Output**: Chunking configuration parameters

3. **Embedding Model Selection**
   - **Unknown**: Primary vs. fallback embedding strategy
   - **Research Focus**:
     - OpenAI text-embedding-3-small performance benchmarks
     - Sentence-transformers MiniLM-L6-v2 local fallback viability
     - Vector dimensionality trade-offs (1536 vs. 384)
     - Cost implications for production scale
   - **Decision Criteria**: Cost, latency, accuracy balance
   - **Output**: Embedding configuration with fallback strategy

4. **Session Management Strategy**
   - **Unknown**: How to persist conversation history for "current session" (FR-005, User Story 2)
   - **Research Focus**:
     - Session storage options (in-memory vs. database)
     - Session expiry policies (time-based vs. interaction-based)
     - Session ID generation and tracking mechanisms
     - Conversation context window for follow-up questions (FR-010)
   - **Decision Criteria**: Stateless API design vs. user experience
   - **Output**: Session management architecture

5. **Rate Limiting Implementation**
   - **Unknown**: Best approach for 20 req/min rate limiting (Constitutional requirement)
   - **Research Focus**:
     - SlowAPI vs. Redis-based rate limiting
     - User identification strategy (IP-based vs. authenticated users)
     - Rate limit enforcement and error handling
     - Graceful degradation strategies
   - **Decision Criteria**: Simplicity vs. scalability
   - **Output**: Rate limiting library and configuration

6. **Deployment Strategy**
   - **Unknown**: Docker containerization setup for FastAPI + Qdrant
   - **Research Focus**:
     - Multi-stage Docker builds for Python applications
     - Qdrant deployment options (local dev vs. cloud production)
     - Neon PostgreSQL connection pooling and configuration
     - Environment variable management and secrets
   - **Decision Criteria**: Development ergonomics vs. production readiness
   - **Output**: Dockerfile and docker-compose.yaml templates

### Research Agents Dispatch

The following research tasks will be executed in Phase 0:

1. ✅ **Task 1**: Research maximum question length limits for chatbot systems and embedding model constraints
2. ✅ **Task 2**: Find best practices for RAG chunking strategies in technical documentation
3. ✅ **Task 3**: Evaluate embedding model performance (OpenAI vs. local fallback) for cost and latency
4. ✅ **Task 4**: Design session management architecture for stateless FastAPI applications
5. ✅ **Task 5**: Compare rate limiting libraries (SlowAPI vs. Redis) for FastAPI
6. ✅ **Task 6**: Research Docker deployment patterns for FastAPI + Qdrant + PostgreSQL

**Output Artifact**: `research.md` with consolidated findings, decisions, rationale, and alternatives considered.

---

## Phase 1: Data Models & Contracts

**Prerequisites**: `research.md` complete with all clarifications resolved

### Data Model Design (`data-model.md`)

**Entities from Spec**:
1. **Message** → Maps to `ChatHistory` in constitution
   - Fields: id, user_id, query, answer, citations (JSON), timestamp
   - Validation: query length (from FR-014), answer non-empty, citations format

2. **Conversation Session** → New model (not in constitution, driven by spec FR-005)
   - Fields: session_id, user_id (optional), created_at, last_activity, state (active/cleared)
   - Relationships: One-to-many with Message

3. **Knowledge Base Entry** → Maps to `Paragraph` in constitution
   - Fields: id, chapter_id (FK), paragraph_index, content, embedding_id (Qdrant point ID)
   - Metadata: chunk_id, chapter_number, section_name, token_count

4. **Query** → Transient model (not persisted)
   - Fields: original_text, normalized_text, conversation_context
   - Purpose: Input validation and preprocessing

**PostgreSQL Tables**:
- `chat_history` (from Message entity)
- `sessions` (from Conversation Session entity)
- `chapters` (from constitution Chapter model)
- `paragraphs` (from constitution Paragraph model, references Qdrant)

**Qdrant Collection**:
- Collection name: `physical_ai_robotics_book`
- Vector size: 1536 (text-embedding-3-small) or 384 (MiniLM fallback)
- Payload schema: chunk_id, chapter_number, chapter_title, paragraph_index, content, section_name, token_count

**Validation Rules**:
- Query length: Max value from FR-014 research
- Empty input: Reject with validation error (FR-007)
- Citation format: `[{"chapter": str, "paragraph": str}]`
- Timestamps: UTC ISO-8601 format

**State Transitions**:
- Session: active → cleared (user action) → terminated (timeout)
- Message: created → stored (immutable)

### API Contracts (`/contracts/`)

**Endpoint Design from Functional Requirements**:

1. **POST /chat** (FR-001, FR-002, FR-003, FR-004)
   - Purpose: Main chatbot query endpoint
   - Input: `ChatRequest { session_id: str, query: str, chapter_filter: Optional[int] }`
   - Output: `ChatResponse { answer: str, citations: List[Citation], query_id: str, processing_time: float }`
   - Errors: 400 (invalid input), 429 (rate limit), 500 (system error)

2. **GET /history/{session_id}** (FR-005, FR-006, FR-009)
   - Purpose: Retrieve conversation history
   - Input: Path parameter `session_id`
   - Output: `HistoryResponse { session_id: str, messages: List[Message], total_count: int }`
   - Errors: 404 (session not found)

3. **DELETE /history/{session_id}** (FR-012)
   - Purpose: Clear conversation history
   - Input: Path parameter `session_id`
   - Output: `ClearResponse { session_id: str, deleted_count: int }`
   - Errors: 404 (session not found)

4. **POST /admin/load_book** (Admin-only, for initial setup)
   - Purpose: Ingest and embed book content
   - Input: `LoadBookRequest { book_path: str, chunk_size: int, overlap: int }`
   - Output: `LoadBookResponse { status: str, chunks_created: int, qdrant_upserted: int }`
   - Errors: 400 (invalid file), 500 (processing error)

5. **GET /health** (Constitutional requirement VI)
   - Purpose: Kubernetes/Docker health check
   - Output: `HealthResponse { status: "healthy" | "degraded", services: {postgres: bool, qdrant: bool} }`

**OpenAPI Schemas**: Generated in `contracts/` folder with full request/response models, validation rules, and error codes.

### Quickstart Guide (`quickstart.md`)

**Purpose**: Enable developers to run the RAG chatbot locally in < 15 minutes.

**Contents**:
1. Prerequisites (Python 3.11+, Docker, OpenAI API key)
2. Environment setup (.env configuration)
3. Database initialization (PostgreSQL + Qdrant)
4. Book ingestion workflow (`POST /admin/load_book`)
5. Testing the chatbot (`POST /chat` with sample queries)
6. Running tests (`pytest backend/tests/`)
7. Common troubleshooting (connection errors, API quota issues)

### Agent Context Update

**Action**: Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`

**Purpose**: Update Claude Code agent context with technology stack decisions from this plan.

**Expected Updates**:
- Add FastAPI, SQLModel, Qdrant, OpenAI SDK to known dependencies
- Reference RAG pipeline architecture for future code generation
- Link to data models and API contracts for consistency

---

## Phase 2: Task Generation (Deferred to `/sp.tasks`)

**Not executed in this command**. After Phase 1 completion, run `/sp.tasks` to generate `tasks.md` with:
- File-level implementation tasks
- Test case definitions
- Acceptance criteria per task
- Dependency ordering

---

## Post-Phase 1 Constitution Re-Check

**Action**: Re-evaluate all 10 constitutional principles after data models and contracts are finalized.

**Focus Areas**:
1. Verify data model alignment with SQLModel schemas (Principle III)
2. Confirm API routes include rate limiting (Principle IV)
3. Validate folder structure matches constitutional layout (Principle V)
4. Ensure health check endpoints are defined (Principle VI)
5. Confirm grounding and citation enforcement in contracts (Principle I)

**Gate**: All principles must PASS before proceeding to `/sp.tasks`. Any new violations must be justified in Complexity Tracking table.

---

## Dependencies & Risks

### External Dependencies
- **Neon PostgreSQL**: Cloud database (requires account + connection string)
- **Qdrant**: Vector database (local Docker or cloud cluster)
- **OpenAI API**: Embeddings + LLM (requires API key + billing)
- **Book Source Content**: "Physical AI & Humanoid Robotics Essentials" text file

### Technical Risks
1. **Risk**: Embedding API costs exceed budget
   - **Mitigation**: Implement local fallback (MiniLM), batch embed during ingestion only
   - **Severity**: Medium (affects cost, not functionality)

2. **Risk**: Qdrant performance degrades with large vector collections
   - **Mitigation**: Use HNSW indexing, optimize `top_k` parameter, consider Qdrant Cloud
   - **Severity**: Low (unlikely with ~1500 chunks)

3. **Risk**: Citation extraction fails for complex book formatting
   - **Mitigation**: Manual metadata tagging during ingestion, fallback to chapter-only citations
   - **Severity**: Medium (affects answer quality)

4. **Risk**: Session persistence across page refreshes (User Story 2, Scenario 2)
   - **Mitigation**: Use database-backed sessions with session cookies or tokens
   - **Severity**: High (affects user experience)

### Non-Technical Risks
1. **Risk**: Book content unavailable or copyrighted
   - **Mitigation**: Use sample chapters for development, clarify licensing with content owner
   - **Severity**: High (blocks ingestion)

2. **Risk**: Scope creep to include quiz/summary generation early
   - **Mitigation**: Strict MVP adherence, defer constitutional extras to Phase 2
   - **Severity**: Medium (affects timeline)

---

## Post-Phase 1 Constitution Re-Check

**Action**: Re-evaluate all 10 constitutional principles after data models, API contracts, and quickstart guide have been finalized.

### Re-Evaluation Results

✅ **I. Grounded Retrieval (RAG-First Architecture)**
- **Status**: PASS
- **Evidence**:
  - API contracts enforce citation format in `ChatResponse` schema (chat.openapi.yaml)
  - Data model includes `citations` JSON field in `ChatHistory` table (data-model.md)
  - Qdrant payload schema includes full `content` text for LLM context
  - Fallback response defined in chat.openapi.yaml examples ("I cannot answer this from the book content")
- **Recommendation**: ✅ Proceed - Fully compliant

---

✅ **II. Performance & Cost Efficiency**
- **Status**: PASS
- **Evidence**:
  - Research.md documents embedding model decision: text-embedding-3-small ($0.02/1M tokens)
  - Cost projection: $32 first month, $2/month recurring (within budget)
  - Local fallback (MiniLM) available for development (zero cost)
  - API contracts include `processing_time_ms` field for monitoring p95 latency
  - Quickstart.md provides configuration for `EMBEDDING_MODEL=local` option
- **Recommendation**: ✅ Proceed - Cost-efficient architecture

---

✅ **III. Data Integrity & Schema Consistency**
- **Status**: PASS
- **Evidence**:
  - All models defined with SQLModel + explicit types (data-model.md)
  - Foreign key relationships documented: `ChatHistory.session_id → Session.session_id`, `Paragraph.chapter_id → Chapter.id`
  - Qdrant payload schema matches PostgreSQL `Paragraph` metadata structure
  - UUID-based IDs prevent auto-increment conflicts (distributed-safe)
  - Alembic migration strategy defined in data-model.md
  - Timestamps enforce UTC ISO-8601 format
- **Recommendation**: ✅ Proceed - Schema consistency enforced

---

✅ **IV. Security & Input Validation**
- **Status**: PASS
- **Evidence**:
  - API contracts enforce `max_length=2000` for query (chat.openapi.yaml)
  - Pydantic validation models prevent SQL injection (SQLModel parameterized queries)
  - Rate limiting documented: 20 req/min (research.md decision: slowapi library)
  - Error responses sanitize sensitive details (admin.openapi.yaml `ErrorResponse` schema)
  - Quickstart.md includes `.env.example` for secrets management (OPENAI_API_KEY)
  - Empty input validation in `Query` transient model (data-model.md)
- **Recommendation**: ✅ Proceed - Security requirements met

---

✅ **V. Clean Architecture & Minimal Dependencies**
- **Status**: PASS
- **Evidence**:
  - Folder structure matches constitutional layout (plan.md Project Structure section)
  - Dependencies documented in research.md: FastAPI, SQLModel, Qdrant, OpenAI, Pydantic, slowapi
  - No circular dependencies in proposed structure (backend/api, backend/models, backend/rag, backend/db)
  - Single responsibility modules: `embedder.py`, `retriever.py`, `reranker.py`, `chunker.py`
  - Quickstart.md uses `requirements.txt` for pinned dependencies
- **Recommendation**: ✅ Proceed - Architecture adheres to constitutional principles

---

✅ **VI. Observability & Production Readiness**
- **Status**: PASS
- **Evidence**:
  - Health check endpoints defined: `/health` and `/ready` (admin.openapi.yaml)
  - `HealthResponse` schema includes service-level status (postgres, qdrant, openai_api)
  - Error responses include `request_id` for correlation (all OpenAPI contracts)
  - `processing_time_ms` field in `ChatHistory` for latency tracking
  - Quickstart.md includes troubleshooting section with log commands
  - Docker deployment strategy documented in research.md (multi-stage builds)
- **Recommendation**: ✅ Proceed - Production readiness requirements met

---

⚠️ **VII. Personalization & User Experience**
- **Status**: DEFERRED (Acknowledged in plan)
- **Evidence**:
  - User personalization (user_level: beginner/intermediate/expert) not in current data models
  - Acknowledged in plan.md Scope Adjustments: "Deferred to post-MVP"
  - Default behavior: Intermediate expertise level for all responses
  - `Session.metadata` JSON field allows future addition without schema migration
- **Recommendation**: ✅ Proceed - Deferral justified; extensibility preserved

---

⚠️ **VIII. Multilingual Support (Urdu Translation)**
- **Status**: DEFERRED (Acknowledged in plan)
- **Evidence**:
  - Urdu translation API route not in current contracts
  - Acknowledged in plan.md Scope Adjustments: "Deferred to post-MVP; prioritize English chatbot first"
  - Future implementation: Separate `/translate` endpoint (constitutional API design already documented)
  - No blocking issues for post-MVP addition
- **Recommendation**: ✅ Proceed - Deferral justified; clear path for future implementation

---

✅ **IX. Hallucination Prevention & Guardrails**
- **Status**: PASS
- **Evidence**:
  - Fallback response defined for no-match scenarios (chat.openapi.yaml example: "I cannot answer this from the book content")
  - Citations required in `ChatResponse` schema (empty array if fallback)
  - `retrieval_score` field in `ChatHistory` for confidence tracking
  - Empty citations trigger fallback message (validated at API layer, to be implemented)
  - Qdrant retrieval filters by `chapter_filter` to scope responses
- **Recommendation**: ✅ Proceed - Guardrails designed into contracts and data models

---

✅ **X. Testing & Quality Assurance**
- **Status**: PASS
- **Evidence**:
  - Quickstart.md Section 6 defines testing workflow: unit, integration, E2E tests
  - Test folder structure documented: `backend/tests/unit`, `backend/tests/integration`, `backend/tests/fixtures`
  - Coverage target: 80%+ (documented in plan.md)
  - Acceptance scenarios from spec.md provide test case foundation
  - Quickstart.md includes pytest commands with coverage reporting
- **Recommendation**: ✅ Proceed - QA requirements defined and actionable

---

### Constitution Re-Check Summary

**Overall Status**: ✅ **PASS** - Ready for `/sp.tasks`

**Breakdown**:
- **8 Principles**: Fully compliant (I, II, III, IV, V, VI, IX, X)
- **2 Principles**: Deferred with justification (VII, VIII - personalization and translation)

**No New Violations**: All deferrals were acknowledged in plan.md Scope Adjustments section and justified as non-MVP features with clear post-MVP implementation paths.

**Recommendations**:
1. ✅ Proceed to `/sp.tasks` - All Phase 1 gates passed
2. Document personalization and Urdu translation as backlog items for post-MVP
3. Ensure implementation phase includes citation validation logic (Principle IX)
4. Set up CI/CD pipeline early to enforce 80% test coverage (Principle X)

---

## Success Criteria (Plan Completion)

✅ **Phase 0 Complete**:
- research.md created with all 6 research tasks resolved
- FR-014 clarification decision documented
- All NEEDS CLARIFICATION markers eliminated

✅ **Phase 1 Complete**:
- data-model.md created with all 4 entities + validation rules
- contracts/ folder contains 3 OpenAPI YAML files (chat, history, admin)
- quickstart.md created with 7-step setup guide
- Agent context updated with technology stack

✅ **Constitution Re-Check Complete**:
- All 10 principles re-evaluated
- No new violations introduced
- Any deferrals justified in Complexity Tracking

✅ **Ready for /sp.tasks**:
- Plan approved by user
- All design artifacts in place
- Technical foundation validated

---

## Next Steps

1. **User Review**: Review this plan for alignment with expectations
2. **Execute Phase 0**: Run research agents to generate research.md
3. **Execute Phase 1**: Generate data-model.md, contracts/, quickstart.md
4. **Update Agent Context**: Run update script
5. **Run /sp.tasks**: Generate implementation task list
6. **Begin Development**: Follow tasks.md for implementation

**Estimated Time to MVP** (after plan approval):
- Phase 0 Research: ~2 hours (automated research + consolidation)
- Phase 1 Design: ~3 hours (data models + contracts + quickstart)
- Phase 2 Tasks: ~1 hour (task generation)
- **Total Planning**: ~6 hours before first line of code

*(Note: No timeline estimates for implementation per project instructions)*
