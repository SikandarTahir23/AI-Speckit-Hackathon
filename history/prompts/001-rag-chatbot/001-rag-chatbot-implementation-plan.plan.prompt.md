---
id: 001
title: RAG Chatbot Implementation Plan
stage: plan
date: 2025-12-13
surface: agent
model: claude-sonnet-4-5
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: spec-driven-development
command: /sp.plan
labels: ["rag", "chatbot", "fastapi", "qdrant", "openai", "architecture", "planning"]
links:
  spec: specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-rag-chatbot/plan.md
  - specs/001-rag-chatbot/research.md
  - specs/001-rag-chatbot/data-model.md
  - specs/001-rag-chatbot/contracts/chat.openapi.yaml
  - specs/001-rag-chatbot/contracts/history.openapi.yaml
  - specs/001-rag-chatbot/contracts/admin.openapi.yaml
  - specs/001-rag-chatbot/quickstart.md
  - CLAUDE.md (updated with tech stack)
tests:
  - No tests run at planning stage
---

## Prompt

```text
read the constitution.md file and start making the chatbot
```

## Response snapshot

Successfully executed the `/sp.plan` command to create a comprehensive implementation plan for the RAG chatbot feature. The plan follows Spec-Driven Development (SDD) principles and constitutional requirements for building a production-grade RAG chatbot system.

### Artifacts Created

**Phase 0 - Research & Design Decisions**:
- `research.md`: Consolidated research findings for 6 key technical decisions
  - Maximum question length: 2000 characters
  - Chunking strategy: 512 tokens with 50-token overlap, sentence-boundary splitting
  - Embedding model: OpenAI text-embedding-3-small (primary) + MiniLM fallback
  - Session management: PostgreSQL-backed with UUID IDs and 24h expiry
  - Rate limiting: slowapi library with in-memory → Redis upgrade path
  - Deployment: Docker multi-stage builds + docker-compose for local dev

**Phase 1 - Data Models & Contracts**:
- `data-model.md`: Complete data model design with 4 entity types
  - PostgreSQL tables: Session, ChatHistory, Chapter, Paragraph
  - Qdrant collection: `physical_ai_robotics_book` (1536-dim vectors)
  - Validation rules, indexes, and migration strategy

- `contracts/chat.openapi.yaml`: Chat API endpoint specification
  - POST /chat: Main chatbot query endpoint with rate limiting
  - Request/response schemas, error codes, examples

- `contracts/history.openapi.yaml`: History management endpoints
  - GET /history/{session_id}: Retrieve conversation history
  - DELETE /history/{session_id}: Clear conversation

- `contracts/admin.openapi.yaml`: Admin & observability endpoints
  - POST /admin/load_book: Book ingestion
  - GET /health: System health check
  - GET /ready: Kubernetes readiness probe

- `quickstart.md`: Developer onboarding guide
  - 7-step setup process (< 15 minutes)
  - Docker compose configuration
  - Sample book content
  - Troubleshooting guide

**Agent Context Update**:
- Updated `CLAUDE.md` with technology stack: Python 3.11+, FastAPI, SQLModel, Qdrant, OpenAI SDK, Sentence Transformers, Pydantic
- Database context: Neon PostgreSQL + Qdrant vector database

**Constitution Compliance**:
- Pre-design check: All 10 principles evaluated (8 PASS, 2 DEFERRED)
- Post-design re-check: All gates passed, deferrals justified
- MVP scope: English chatbot with core functionality
- Post-MVP backlog: User personalization, Urdu translation, quiz generation

### Key Decisions

1. **Architecture**: Web application with FastAPI backend + future frontend integration (existing Docusaurus site)
2. **Technology Stack**: Python 3.11+, FastAPI, SQLModel, PostgreSQL, Qdrant, OpenAI Agents SDK
3. **Deployment**: Docker containerization with multi-stage builds, docker-compose for dev
4. **Scope**: MVP focuses on core RAG chatbot; defers personalization and translation
5. **Cost**: ~$32 first month (embedding costs), ~$2/month recurring

### Plan Structure

- **Technical Context**: Language, dependencies, storage, testing, performance targets
- **Constitution Check**: Pre-design evaluation of all 10 principles
- **Project Structure**: Backend folder layout following constitutional architecture
- **Phase 0**: Research resolving all NEEDS CLARIFICATION markers (6 tasks)
- **Phase 1**: Data models, API contracts, quickstart guide
- **Constitution Re-Check**: Post-design compliance validation
- **Dependencies & Risks**: External services, technical/non-technical risks with mitigations

## Outcome

- ✅ Impact: Complete implementation plan ready for task generation (`/sp.tasks`)
- 🧪 Tests: Planning artifacts validated; no code tests at this stage
- 📁 Files: 7 artifacts created (plan.md, research.md, data-model.md, 3 OpenAPI contracts, quickstart.md)
- 🔁 Next prompts: `/sp.tasks` to generate tasks.md with implementation tasks
- 🧠 Reflection: Comprehensive planning phase completed following SDD methodology; all constitutional gates passed; clear MVP scope with post-MVP backlog

## Evaluation notes (flywheel)

- Failure modes observed: None; plan execution successful
- Graders run and results (PASS/FAIL): PASS - All constitutional principles evaluated and documented
- Prompt variant (if applicable): N/A - Standard `/sp.plan` workflow
- Next experiment (smallest change to try): Proceed to `/sp.tasks` for task generation
