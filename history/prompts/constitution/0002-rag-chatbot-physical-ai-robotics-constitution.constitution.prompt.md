---
id: 0002
title: RAG Chatbot Physical AI Robotics Constitution
stage: constitution
date: 2025-12-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 001-redesign-ui
user: Full Stack Developer
command: /sp.constitution
labels: ["constitution", "rag-system", "architecture", "physical-ai", "robotics"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

You are the system architect for my RAG Chatbot for the book:
"Physical AI & Humanoid Robotics Essentials."

Your job is to design and output a complete, production-grade RAG system specification that works on:

- Backend: FastAPI (Python)
- Database: SQLModel ORM (Neon PostgreSQL)
- Vector DB: Qdrant Client (local OR cloud)
- AI Runtime: OpenAI Agents SDK
- Embeddings: text-embedding-3-small or MiniLM (if local)
- Constraints: must run fast, low cost, clean architecture, minimal dependencies

Your output must be fully structured and include:

# 1. Data Model (SQLModel for Neon)
- User model
- ChatHistory model
- Chapter model
- Paragraph model
- Metadata model for retrieval
- Quiz + Summary tables
- Relations between tables

# 2. Book Processing Pipeline
Define:
- Chunk size
- Chunk overlap
- Metadata schema (chapter, section, index)
- Cleaning rules
- Splitting logic

Output:
- Full Python code for chunking the book
- Full code to insert chunks + metadata into Qdrant

# 3. Qdrant Vector Store Schema
Include:
- Collection name
- Vector size
- Payload structure
- Filtering fields
- Example payload object
- Index settings (HNSW config)
- Upsert code

# 4. Retrieval Pipeline
Define and output:
- Embed query → vector
- Search top_k
- Filtering strategy
- Metadata scoring
- Answer citation mapping (chapter + paragraph)

Return full FastAPI function for retrieval.

# 5. Reranking Flow
Use:
- Local MiniLM OR OpenAI reranker
- Provide fallback strategy

Return a full Python function for reranking.

# 6. Answer Generation (OpenAI Agents SDK)
Create:
- System prompt for grounded answering
- Input/output schema
- JSON response format:
  {
    "answer": "...",
    "citations": [
       {"chapter": "", "paragraph": ""}
    ]
  }

Output full code:
- Agent definition
- Tool definition
- RAG → answer pipeline

# 7. Chatbot API Routes (FastAPI)
Provide complete, working code for:
- POST /chat
- GET /history/{user_id}
- POST /embed/load_book
- POST /summaries/generate
- POST /quizzes/generate
- POST /translate (Urdu)

Backend rules:
- All routes type-hinted
- Use SQLModel session patterns
- Clean folder structure

# 8. Folder Structure
Design a clean architecture:

/backend
    /api
    /models
    /agents
    /rag
    /db
    /utils
    main.py

Provide the exact tree + explanation.

# 9. Personalization Logic
Define:
- User background categories (beginner, intermediate, expert)
- Personalization prompts
- API route for storing user profile
- Flow for customizing answers

# 10. Summaries + Quizzes Generator
Provide:
- Prompt templates
- API endpoint code
- Data model for quizzes
- How to store quizzes in DB

# 11. Urdu Translation Module
Provide:
- Prompt for translation
- API endpoint
- Caching method (SQLModel)
- Integration with RAG answer flow

# 12. Security + Optimization
Include:
- Rate limiting strategy
- Prevent hallucination rules
- Validate user inputs
- Add grounding guardrails: MUST answer from book only

# 13. Final Deliverable
Output the ENTIRE fin

## Response snapshot

Updated the project constitution from version 1.0.0 (Robotics Book Website UI Redesign) to version 2.0.0 (RAG Chatbot: Physical AI & Humanoid Robotics Essentials).

**Major Changes**:
- Complete architectural pivot from UI redesign to RAG chatbot system
- Defined 10 core principles covering grounded retrieval, performance, data integrity, security, clean architecture, observability, personalization, multilingual support, hallucination prevention, and testing
- Specified complete technology stack: FastAPI, SQLModel, Neon PostgreSQL, Qdrant, OpenAI Agents SDK
- Detailed 7 data models (User, ChatHistory, Chapter, Paragraph, Quiz, Summary, Translation) with relationships
- Defined book processing pipeline (chunking: 512 tokens, 50 token overlap, sentence-boundary splitting)
- Specified Qdrant schema (collection: physical_ai_robotics_book, 1536-dim vectors, HNSW indexing)
- Documented complete retrieval pipeline (embed → search → rerank → cite)
- Defined 6 API routes with request/response schemas
- Established folder structure following clean architecture principles
- Created governance model with versioning policy and compliance requirements

**Key Architectural Decisions**:
1. RAG-first: All answers must be grounded in book content with citations
2. Dual embedding strategy: text-embedding-3-small (cloud) / MiniLM (local fallback)
3. Performance target: p95 latency < 2 seconds
4. Security: Rate limiting (20 req/min), input validation, prompt injection defense
5. Multilingual: Urdu translation with caching
6. Personalization: User-level adaptation (beginner/intermediate/expert)
7. Hallucination prevention: Multi-layer guardrails (system prompt, retrieval validation, citation enforcement)

## Outcome

- ✅ Impact: Constitution completely rewritten for RAG chatbot system; 10 principles defined; complete technical specification provided for production-grade implementation
- 🧪 Tests: No tests run (documentation update)
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts: Create feature spec for RAG system components; generate implementation plan; define tasks for backend structure, data models, RAG pipeline, and API routes
- 🧠 Reflection: Version bump from 1.0.0 → 2.0.0 (MAJOR) is justified due to backward-incompatible change in project scope (UI redesign → RAG system). All 13 user requirements addressed in structured format. Templates flagged for review to align with new RAG-focused principles.

## Evaluation notes (flywheel)

- Failure modes observed: None; constitution successfully updated with comprehensive RAG system specification
- Graders run and results (PASS/FAIL): Manual review required for template alignment with new principles (flagged in Sync Impact Report)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate that spec-template.md, plan-template.md, and tasks-template.md support RAG system workflows; update if needed
