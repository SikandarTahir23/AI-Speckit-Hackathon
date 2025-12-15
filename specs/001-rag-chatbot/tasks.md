# Implementation Tasks: RAG Chatbot

**Feature**: RAG Chatbot for "Physical AI & Humanoid Robotics Essentials"
**Branch**: `001-rag-chatbot`
**Generated**: 2025-12-13
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Overview

This document contains implementation tasks organized by user story priority. Each user story represents an independently testable increment that delivers value.

**Total Tasks**: 62
**Parallel Opportunities**: 28 tasks marked with [P]
**Test Coverage Target**: 80%+ (pytest)

---

## Task Execution Strategy

### MVP Scope (Recommended First Delivery)

**User Story 1 only** - Ask Question and Get Answer (P1)
- Delivers core value: Users can ask questions and get grounded answers
- ~18 tasks (Setup + Foundational + US1)
- Estimated: Smallest viable increment

### Full Feature Scope

All 5 user stories in priority order (P1 → P2 → P3)
- Complete chatbot with history, error handling, and convenience features
- 62 total tasks across 7 phases

---

## Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US1: Ask Question) ← MVP DELIVERABLE
    ↓
Phase 4 (US2: View History) + Phase 5 (US3: Handle Errors) ← Can run in parallel
    ↓
Phase 6 (US4: Clear History) + Phase 7 (US5: Copy Answer) ← Can run in parallel
    ↓
Phase 8 (Polish & Cross-Cutting)
```

**Note**: User Stories 2-5 are independent after Phase 2 completes. They can be implemented in any order or in parallel.

---

## Phase 1: Setup & Project Initialization

**Goal**: Initialize project structure, dependencies, and development environment
**Blocks**: All subsequent phases
**Independent Test**: `docker-compose up` successfully starts all services

### Tasks

- [ ] T001 Create backend directory structure per plan.md (backend/api, backend/models, backend/rag, backend/db, backend/utils, backend/tests)
- [ ] T002 [P] Create requirements.txt with pinned dependencies (FastAPI==0.104.1, SQLModel==0.0.14, Qdrant-client==1.7.0, openai==1.3.7, sentence-transformers==2.2.2, pydantic==2.5.0, slowapi==0.1.9, pytest==7.4.3, alembic==1.12.1)
- [ ] T003 [P] Create .env.example file in backend/ with all required environment variables per quickstart.md
- [ ] T004 [P] Create Dockerfile with multi-stage build per research.md deployment strategy in backend/
- [ ] T005 [P] Create docker-compose.yml in project root with PostgreSQL, Qdrant, and app services per quickstart.md
- [ ] T006 [P] Create backend/main.py with FastAPI app initialization and CORS configuration
- [ ] T007 [P] Create backend/utils/config.py with Pydantic BaseSettings for environment variable management
- [ ] T008 [P] Create backend/utils/logger.py with structured logging setup (JSON format, correlation IDs)
- [ ] T009 Create sample book content file in backend/data/book_source/physical_ai_robotics.md per quickstart.md Step 2.3

**Completion Criteria**:
- ✅ All directories exist with __init__.py files
- ✅ `docker-compose up` starts PostgreSQL (port 5432), Qdrant (port 6333), app (port 8000)
- ✅ FastAPI app returns 404 for unknown routes (confirms app is running)
- ✅ .env.example documented with all required variables

---

## Phase 2: Foundational Infrastructure

**Goal**: Set up database models, connections, and core RAG pipeline components
**Blocks**: All user story implementations
**Independent Test**: Database migrations run successfully; Qdrant collection created; embedding test passes

### Database Models & Migrations

- [ ] T010 Create backend/models/session.py with Session SQLModel schema per data-model.md Section 1
- [ ] T011 [P] Create backend/models/chat.py with ChatHistory and Citation SQLModel schemas per data-model.md Section 2
- [ ] T012 [P] Create backend/models/book.py with Chapter and Paragraph SQLModel schemas per data-model.md Sections 3-4
- [ ] T013 Create backend/db/postgres.py with PostgreSQL connection, session management, and engine configuration
- [ ] T014 Initialize Alembic in backend/db/migrations/ and create initial migration for all models
- [ ] T015 Create backend/db/qdrant_client.py with Qdrant connection, collection creation, and HNSW configuration per data-model.md Qdrant section

### RAG Pipeline Core Components

- [ ] T016 [P] Create backend/rag/embedder.py with dual embedding strategy (OpenAI + MiniLM fallback) per research.md Task 3
- [ ] T017 [P] Create backend/rag/chunker.py with 512-token chunking, 50-token overlap, sentence-boundary splitting per research.md Task 2
- [ ] T018 [P] Create backend/rag/retriever.py with Qdrant search (top_k=10), chapter filtering, and metadata extraction
- [ ] T019 [P] Create backend/rag/reranker.py with cross-encoder reranking (MiniLM) to select top 5 from top 10 results
- [ ] T020 Create backend/utils/validators.py with input validation functions (query length 2000 chars, empty input check per research.md Task 1)

### API Infrastructure

- [ ] T021 Create backend/api/dependencies.py with database session dependency injection and rate limiter setup
- [ ] T022 Implement slowapi rate limiting (20 req/min) in backend/api/dependencies.py per research.md Task 5
- [ ] T023 [P] Create backend/api/routes.py with FastAPI router registration and error handler registration

**Completion Criteria**:
- ✅ Alembic migrations run: `alembic upgrade head` creates all tables
- ✅ Qdrant collection exists: `curl http://localhost:6333/collections/physical_ai_robotics_book` returns collection info
- ✅ Embedding test: Embed sample text with both OpenAI and local models successfully
- ✅ Chunking test: Process sample book chapter into 512-token chunks
- ✅ Rate limiter test: 21st request within 1 minute returns HTTP 429

---

## Phase 3: User Story 1 - Ask Question and Get Answer (Priority: P1)

**Goal**: Core MVP - Users can ask questions and receive grounded, citation-backed answers
**Independent Test**: POST /chat with sample question returns answer with citations within 3 seconds
**Delivers**: FR-001, FR-002, FR-003, FR-004, SC-001, SC-002, SC-003

### Book Ingestion (Admin Endpoint)

- [ ] T024 [US1] Implement POST /admin/load_book endpoint in backend/api/routes.py per admin.openapi.yaml
- [ ] T025 [US1] Create book processing service in backend/rag/chunker.py:process_book() that parses markdown, extracts chapters, and chunks content
- [ ] T026 [US1] Implement embedding generation in backend/rag/embedder.py:embed_chunks() with batch processing (100 chunks/batch)
- [ ] T027 [US1] Implement Qdrant upsert in backend/db/qdrant_client.py:upsert_chunks() with retry logic
- [ ] T028 [US1] Implement PostgreSQL insert in backend/db/postgres.py:insert_paragraphs() for Chapter and Paragraph records

### RAG Agent Implementation

- [ ] T029 [US1] Create backend/agents/rag_agent.py with OpenAI Agent SDK configuration and system prompt per plan.md constitution
- [ ] T030 [US1] Create backend/agents/tools.py with retrieval tool and citation formatting tool for agent
- [ ] T031 [US1] Implement answer generation in backend/agents/rag_agent.py:generate_answer() with context assembly and LLM call

### Chat Endpoint Implementation

- [ ] T032 [US1] Implement POST /chat endpoint in backend/api/routes.py per chat.openapi.yaml
- [ ] T033 [US1] Implement query validation in backend/api/routes.py using validators.py (max 2000 chars, non-empty)
- [ ] T034 [US1] Implement session creation logic: generate UUID session_id if not provided, insert into sessions table
- [ ] T035 [US1] Implement RAG pipeline orchestration in POST /chat: embed query → retrieve → rerank → generate → save to chat_history
- [ ] T036 [US1] Implement response assembly in POST /chat: format ChatResponse with answer, citations, query_id, session_id, processing_time_ms
- [ ] T037 [US1] Implement error handling in POST /chat: catch Qdrant errors, OpenAI errors, database errors, return appropriate HTTP status codes per chat.openapi.yaml ErrorResponse

### Testing & Validation

- [ ] T038 [US1] Create backend/tests/unit/test_embedder.py with tests for OpenAI and local embedding generation
- [ ] T039 [US1] [P] Create backend/tests/unit/test_chunker.py with tests for 512-token chunking and overlap logic
- [ ] T040 [US1] [P] Create backend/tests/unit/test_retriever.py with tests for Qdrant search and chapter filtering
- [ ] T041 [US1] [P] Create backend/tests/unit/test_reranker.py with tests for top-5 reranking from top-10 results
- [ ] T042 [US1] Create backend/tests/integration/test_chat_endpoint.py with tests for POST /chat success, validation errors, rate limiting
- [ ] T043 [US1] Create backend/tests/integration/test_rag_pipeline.py with end-to-end test: question → answer with citations

**Completion Criteria**:
- ✅ Book ingestion: POST /admin/load_book processes sample book (8 chapters) and returns 200 with chunks_created count
- ✅ Chat endpoint: POST /chat returns answer with citations for "What are hydraulic actuators?" within 3 seconds
- ✅ Citations: Answer includes at least 1 citation with chapter and section references
- ✅ Validation: POST /chat with empty query returns 400 with validation error
- ✅ Rate limiting: 21st request within 1 minute returns 429 with Retry-After header
- ✅ Tests pass: pytest backend/tests/ shows 80%+ coverage for US1 code

**US1 Test Scenarios** (From Spec):
1. ✅ Given chatbot loaded, When user asks "What are hydraulic actuators?", Then answer returned within 3 seconds with relevant content
2. ✅ Given answer displayed, When user reads response, Then answer sourced from knowledge base with citations
3. ✅ Given answer displayed, When user reads response, Then answer is clear and addresses question

---

## Phase 4: User Story 2 - View Conversation History (Priority: P2)

**Goal**: Users can retrieve and review their conversation history
**Independent Test**: GET /history/{session_id} returns all Q&A pairs in chronological order
**Delivers**: FR-005, FR-006, FR-009, SC-004, SC-005

### History Endpoint Implementation

- [ ] T044 [US2] Implement GET /history/{session_id} endpoint in backend/api/routes.py per history.openapi.yaml
- [ ] T045 [US2] Implement session existence check in GET /history: query sessions table, return 404 if not found
- [ ] T046 [US2] Implement message retrieval in GET /history: query chat_history table filtered by session_id, ordered by timestamp ASC
- [ ] T047 [US2] Implement pagination in GET /history: support limit (default 50) and offset (default 0) query parameters
- [ ] T048 [US2] Implement response assembly in GET /history: format HistoryResponse with messages array, total_count, limit, offset

### Testing

- [ ] T049 [US2] Create backend/tests/integration/test_history_endpoint.py with tests for GET /history success, empty history, session not found, pagination

**Completion Criteria**:
- ✅ History retrieval: GET /history/{session_id} after 3 chat messages returns all 3 messages in chronological order
- ✅ Pagination: GET /history/{session_id}?limit=2 returns 2 messages with total_count=3
- ✅ Not found: GET /history/invalid-uuid returns 404 with error message
- ✅ Tests pass: pytest backend/tests/integration/test_history_endpoint.py passes all tests

**US2 Test Scenarios** (From Spec):
1. ✅ Given user asked 3 questions, When scrolling history, Then all Q&A pairs visible in chronological order
2. ✅ Given conversation exists, When page refreshes, Then history persists (session retrieved from DB)
3. ✅ Given long conversation, When displaying messages, Then most recent message visible (handled by frontend, backend returns correct order)

---

## Phase 5: User Story 3 - Handle Unclear/Out-of-Scope Questions (Priority: P2)

**Goal**: Chatbot provides helpful fallback responses for unanswerable questions
**Independent Test**: POST /chat with out-of-scope question returns fallback message without citations
**Delivers**: FR-008, SC-007

### Fallback Logic Implementation

- [ ] T050 [US3] Implement retrieval score threshold check in backend/rag/retriever.py: if top score < 0.7, flag as low-confidence
- [ ] T051 [US3] Implement fallback response logic in backend/agents/rag_agent.py: if low-confidence or no results, return "I cannot answer this from the book content" message
- [ ] T052 [US3] Update POST /chat to check for empty citations and return fallback response with empty citations array
- [ ] T053 [US3] Add retrieval_score field to ChatHistory table insert in POST /chat for confidence tracking

### Testing

- [ ] T054 [US3] Create backend/tests/integration/test_fallback_responses.py with tests for out-of-scope questions, low retrieval scores, empty knowledge base scenarios

**Completion Criteria**:
- ✅ Out-of-scope: POST /chat with "What's the weather?" returns fallback message: "I cannot answer this from the book content"
- ✅ Empty citations: Fallback response has citations=[] array
- ✅ Retrieval score: ChatHistory record includes retrieval_score field (null or <0.7 for fallback)
- ✅ Tests pass: pytest backend/tests/integration/test_fallback_responses.py passes all tests

**US3 Test Scenarios** (From Spec):
1. ✅ Given knowledge base has product docs, When user asks "What's the weather?", Then fallback message with contact info returned
2. ✅ Given no relevant information, When chatbot searches, Then limitation acknowledged within 3 seconds (no hallucination)
3. ✅ Given fallback triggered, When displaying message, Then alternative help options provided (contact info in response)

---

## Phase 6: User Story 4 - Clear Conversation and Start Fresh (Priority: P3)

**Goal**: Users can clear their conversation history to start a new topic
**Independent Test**: DELETE /history/{session_id} removes all messages and marks session as cleared
**Delivers**: FR-012

### Clear History Endpoint Implementation

- [ ] T055 [US4] Implement DELETE /history/{session_id} endpoint in backend/api/routes.py per history.openapi.yaml
- [ ] T056 [US4] Implement session state update in DELETE /history: set state='cleared' in sessions table
- [ ] T057 [US4] Implement message deletion in DELETE /history: delete all chat_history records for session_id
- [ ] T058 [US4] Implement response assembly in DELETE /history: format ClearResponse with session_id, deleted_count, confirmation message

### Testing

- [ ] T059 [US4] Create backend/tests/integration/test_clear_history.py with tests for DELETE /history success, already cleared, session not found

**Completion Criteria**:
- ✅ Clear history: DELETE /history/{session_id} after 5 messages returns deleted_count=5
- ✅ State update: Session record has state='cleared' after DELETE
- ✅ Idempotency: Second DELETE /history/{session_id} returns 409 conflict (already cleared)
- ✅ Tests pass: pytest backend/tests/integration/test_clear_history.py passes all tests

**US4 Test Scenarios** (From Spec):
1. ✅ Given active conversation, When user clicks "Clear", Then messages removed and fresh interface shown (backend: deleted_count > 0)
2. ✅ Given conversation cleared, When new question asked, Then no context from previous conversation (new session_id or state=cleared prevents context retrieval)
3. ✅ Given clear button visible, When no messages, Then button disabled (handled by frontend, backend always accepts DELETE)

---

## Phase 7: User Story 5 - Copy Answer Text (Priority: P3)

**Goal**: Users can copy chatbot answers to clipboard
**Independent Test**: N/A - Frontend-only feature (no backend changes required)
**Delivers**: FR-013, SC-006

### Notes

**This user story is frontend-only** and does not require backend implementation tasks. The backend already provides answer text in ChatResponse.answer field.

Frontend implementation (out of scope for backend tasks):
- Add "Copy" button next to each answer in UI
- Implement clipboard API: `navigator.clipboard.writeText(answer)`
- Show "Copied!" tooltip on success
- Handle errors (clipboard permission denied)

**Completion Criteria**:
- ✅ No backend changes required - answer text already available in API response
- ✅ Frontend team can implement copy functionality using ChatResponse.answer field

**US5 Test Scenarios** (From Spec):
1. ✅ Given answer displayed, When "Copy" clicked, Then text copied to clipboard (frontend test)
2. ✅ Given text copied, When pasted, Then plain text without styling (frontend clipboard API handles this)
3. ✅ Given copy succeeds, When button clicked, Then "Copied!" feedback shown (frontend UI feedback)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Finalize observability, error handling, and production readiness
**Blocks**: None (can run anytime after Phase 2)
**Independent Test**: Health checks return correct status; logs are structured; errors are handled gracefully

### Observability & Health Checks

- [ ] T060 [P] Implement GET /health endpoint in backend/api/routes.py per admin.openapi.yaml with PostgreSQL, Qdrant, OpenAI API health checks
- [ ] T061 [P] Implement GET /ready endpoint in backend/api/routes.py with readiness checks (DB connected, Qdrant collection exists, knowledge base loaded)
- [ ] T062 [P] Add structured logging with correlation IDs to all API routes in backend/api/routes.py using logger.py

**Completion Criteria**:
- ✅ Health check: GET /health returns status="healthy" when all services operational
- ✅ Readiness check: GET /ready returns 503 if knowledge base empty (no chunks in Qdrant)
- ✅ Logs: All API calls log request_id, endpoint, status_code, processing_time_ms in JSON format
- ✅ Error handling: All unhandled exceptions return 500 with ErrorResponse format and are logged

---

## Parallel Execution Examples

### Phase 1 (Setup) - Parallel Opportunities

**Can run in parallel** (different files, no dependencies):
- T002 (requirements.txt), T003 (.env.example), T004 (Dockerfile), T005 (docker-compose.yml), T006 (main.py), T007 (config.py), T008 (logger.py)

**Must run sequentially**:
- T001 (directory structure) → THEN → T002-T009 (files within directories)

### Phase 2 (Foundational) - Parallel Opportunities

**Can run in parallel** (independent models/modules):
- T011 (chat.py), T012 (book.py), T016 (embedder.py), T017 (chunker.py), T018 (retriever.py), T019 (reranker.py), T020 (validators.py), T023 (routes.py)

**Must run sequentially**:
- T010 (session.py) → T013 (postgres.py) → T014 (migrations) [database setup]
- T015 (qdrant_client.py) requires T016 (embedder.py) for testing

### Phase 3 (US1) - Parallel Opportunities

**Can run in parallel** (independent test files):
- T038 (test_embedder.py), T039 (test_chunker.py), T040 (test_retriever.py), T041 (test_reranker.py)

**Must run sequentially**:
- T024-T028 (book ingestion) → T042 (test_chat_endpoint.py needs loaded book)
- T029-T031 (RAG agent) → T032-T037 (chat endpoint uses agent)

### Phases 4-7 (US2-US5) - Parallel Opportunities

**User Stories 2, 3, 4 can be implemented in parallel** after Phase 2 completes:
- Phase 4 (US2) + Phase 5 (US3) + Phase 6 (US4) are independent
- Example: 3 developers can work on US2, US3, US4 simultaneously

---

## Dependency Graph

```
Setup (Phase 1)
    ↓
Foundational (Phase 2)
    ├─→ US1: Ask Question (Phase 3) ← MVP
    ├─→ US2: View History (Phase 4) ─┐
    ├─→ US3: Handle Errors (Phase 5) ├→ Can run in parallel
    └─→ US4: Clear History (Phase 6) ─┘
         US5: Copy Answer (Phase 7) ← Frontend-only, no backend tasks
    ↓
Polish (Phase 8) ← Can run anytime after Phase 2
```

---

## Implementation Strategy

### Recommended Approach: Incremental Delivery

1. **Sprint 1 - MVP (US1 only)**:
   - Complete Phases 1, 2, 3 (Setup → Foundational → US1)
   - ~18 tasks, delivers core Q&A functionality
   - Deploy and validate with users

2. **Sprint 2 - Enhanced UX (US2 + US3)**:
   - Complete Phases 4, 5 (History + Error Handling)
   - ~11 tasks, improves user experience significantly

3. **Sprint 3 - Convenience Features (US4 + US5 + Polish)**:
   - Complete Phases 6, 7, 8 (Clear, Copy, Observability)
   - ~8 tasks, adds convenience and production readiness

### Alternative: Big Bang Delivery

Complete all phases sequentially (1 → 2 → 3 → 4 → 5 → 6 → 7 → 8)
- All 62 tasks in one release
- Higher risk, longer time to value

---

## Task Summary

| Phase | User Story | Priority | Task Count | Parallel Tasks | Independent Test Criteria |
|-------|------------|----------|------------|----------------|---------------------------|
| 1 | Setup | - | 9 | 7 | `docker-compose up` successful |
| 2 | Foundational | - | 14 | 8 | Migrations run, Qdrant collection exists |
| 3 | US1 | P1 | 20 | 4 | POST /chat returns answer with citations |
| 4 | US2 | P2 | 6 | 0 | GET /history returns chronological messages |
| 5 | US3 | P2 | 5 | 0 | Fallback response for out-of-scope questions |
| 6 | US4 | P3 | 5 | 0 | DELETE /history clears messages |
| 7 | US5 | P3 | 0 | 0 | Frontend-only (no backend tasks) |
| 8 | Polish | - | 3 | 3 | Health checks return correct status |
| **Total** | - | - | **62** | **22** | - |

---

## Task Format Validation

✅ All tasks follow required format: `- [ ] T### [P?] [US#?] Description with file path`
✅ All user story tasks include [US#] label
✅ All parallelizable tasks include [P] marker
✅ All task IDs are sequential (T001-T062)
✅ All tasks include specific file paths for implementation

---

## Next Steps

1. **Review & Approve**: Validate task breakdown aligns with feature requirements
2. **Prioritize**: Confirm MVP scope (recommend US1 only for first delivery)
3. **Assign**: Distribute tasks to development team
4. **Execute**: Follow task order, mark checkboxes as completed
5. **Test**: Run pytest after each phase to validate coverage and correctness
6. **Deploy**: Use Docker deployment strategy from research.md

---

**Ready to implement! Start with Phase 1 (Setup) and progress through phases sequentially or jump to MVP (US1) after Phase 2.** 🚀
