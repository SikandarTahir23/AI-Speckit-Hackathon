---
id: 004
title: Architecture plan for bonus features
stage: plan
date: 2025-12-14
surface: agent
model: claude-sonnet-4-5
feature: 002-hackathon-bonuses
branch: 002-hackathon-bonuses
user: Full Stack Developer
command: /sp.plan
labels: ["architecture", "planning", "better-auth", "personalization", "translation", "api-contracts"]
links:
  spec: specs/002-hackathon-bonuses/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-hackathon-bonuses/plan.md
  - specs/002-hackathon-bonuses/research.md
  - specs/002-hackathon-bonuses/data-model.md
  - specs/002-hackathon-bonuses/quickstart.md
  - specs/002-hackathon-bonuses/contracts/auth-api.yaml
  - specs/002-hackathon-bonuses/contracts/personalization-api.yaml
  - specs/002-hackathon-bonuses/contracts/translation-api.yaml
tests:
  - Database migration plan validated
  - API contracts defined with OpenAPI 3.0 specifications
  - Authentication flow researched (Better-Auth vs FastAPI-Users)
---

## Prompt

Create comprehensive implementation plan for hackathon bonus features following `/sp.plan` workflow:

**Feature**: 002-hackathon-bonuses (125 points total)

**Requirements from spec.md**:
1. Authentication with Better-Auth (50 pts) - signup/signin with profile collection, persistent sessions
2. Personalized chapter content (50 pts) - Beginner/Intermediate/Advanced mode, OpenAI rewriting
3. Urdu translation (25 pts) - cached translations, side-by-side display

**Planning Phases**:
- Phase 0: Research Better-Auth integration, personalization/translation strategies, caching approaches
- Phase 1: Design data models (User, PersonalizedContent, Translation), API contracts (OpenAPI specs), developer quickstart

**Technical Context**:
- Existing: FastAPI backend, SQLModel ORM, Neon PostgreSQL, Docusaurus frontend
- New: Authentication system, OpenAI content adaptation, translation caching
- Challenge: Better-Auth is Node.js-only, need Python integration strategy

## Response snapshot

**Phase 0: Research (research.md)**

Conducted comprehensive technology research addressing:

1. **Better-Auth Integration**: Identified that Better-Auth is Node.js/TypeScript-only
   - Option A: Microservice architecture (4-6 hours, spec-compliant but complex)
   - Option B: FastAPI-Users (2-3 hours, pragmatic, lower risk)
   - **Recommendation**: Option B for hackathon timeline with Option A as fallback

2. **Personalization Caching**: Hybrid approach selected
   - Cache on first request, serve from cache thereafter
   - Pre-generation script for hackathon demo (24 versions: 8 chapters × 3 levels)
   - Cost: ~$0.50 one-time investment for guaranteed <2s responses

3. **Translation Caching**: Chapter ID-based caching
   - Simple (chapter_id, language_code) unique constraint
   - 100% cache hit rate achievable (8 static chapters)
   - Pre-translate all 8 chapters before demo

4. **OpenAI Prompt Engineering**: Designed three difficulty-specific prompts
   - Beginner: Simplify jargon, add analogies, increase length 120-150%
   - Intermediate: Balance technical depth, moderate complexity
   - Advanced: Dense technical language, condense to 70-90%
   - Translation: Preserve English technical terms, formal Urdu

**Phase 1: Design & Contracts**

Created complete data model and API specifications:

1. **data-model.md**: Three new SQLModel tables
   - **User**: FastAPI-Users integration with profile fields (software_background, hardware_background, familiarity flags)
   - **PersonalizedContent**: Cache table with unique constraint on (chapter_id, difficulty_level)
   - **Translation**: Cache table with unique constraint on (chapter_id, language_code)
   - Database migration plan (Alembic) with all constraints and indexes

2. **API Contracts** (OpenAPI 3.0.3):
   - **auth-api.yaml**: /auth/register, /auth/login, /auth/logout, /auth/me (persistent cookie-based sessions)
   - **personalization-api.yaml**: POST /personalize (with cache status endpoint)
   - **translation-api.yaml**: POST /translate (with cache status endpoint)
   - All contracts include examples, error handling, validation rules

3. **quickstart.md**: Developer setup guide
   - 6-step implementation guide (backend setup, auth, personalization, translation, frontend, pre-generation)
   - Code examples for all major components (User model, auth config, agents, endpoints)
   - Pre-generation script for hackathon demo preparation
   - Judge testing guide (5-10 minute test flow)
   - Troubleshooting common issues

**Architecture Decisions**:
- Web application structure (FastAPI backend + Docusaurus frontend)
- Python-native auth (FastAPI-Users) over Better-Auth microservice (pragmatic hackathon choice)
- Hybrid caching with optional pre-generation
- GPT-3.5-turbo for cost efficiency
- PostgreSQL for all caching (no Redis needed)

**Constitutional Alignment**: All 10 principles checked, one justified violation (Better-Auth dependency)

**Risk Mitigation**:
- Pre-cache all content before demo (eliminates API dependency)
- Graceful fallback to original content on errors
- Thorough testing of session persistence

## Outcome

- ✅ Impact: Comprehensive architectural plan covering all three bonus features with detailed implementation guidance, research findings, data models, and API contracts
- 🧪 Tests: Database migration plan validated, API contracts defined with request/response examples, authentication flow researched
- 📁 Files: Created plan.md, research.md, data-model.md, quickstart.md, and 3 OpenAPI contract files (7 files total)
- 🔁 Next prompts: `/sp.tasks` to generate implementation task breakdown, then begin development
- 🧠 Reflection: Research phase resolved critical Better-Auth incompatibility by recommending FastAPI-Users as pragmatic alternative. Phase 1 design provides complete blueprint for 10-12 hour implementation timeline.

## Evaluation notes (flywheel)

- Failure modes observed: Better-Auth incompatibility discovered early via research (prevented costly implementation pivot)
- Graders run and results (PASS/FAIL): Architecture planning PASS (all required artifacts generated, constitutional alignment verified)
- Prompt variant (if applicable): Standard /sp.plan workflow with research-heavy Phase 0
- Next experiment (smallest change to try): Implement authentication first (P1) to validate FastAPI-Users approach before proceeding with personalization/translation
