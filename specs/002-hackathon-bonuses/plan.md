# Implementation Plan: Hackathon Bonus Features

**Branch**: `002-hackathon-bonuses` | **Date**: 2025-12-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/002-hackathon-bonuses/spec.md`

## Summary

Implement three hackathon bonus features (125 points total) for the Physical AI & Humanoid Robotics textbook: (1) **Authentication & User Profiling** using Better-Auth with technical background collection stored in Neon PostgreSQL via SQLModel, supporting persistent sessions across browser restarts (50 points); (2) **Personalized Chapter Content** where users select difficulty level (Beginner/Intermediate/Advanced) and OpenAI rewrites chapter content to match their expertise (50 points); (3) **Urdu Translation** with cached translations displayed side-by-side with English content (25 points).

**Technical Approach**: Extend existing FastAPI backend with Better-Auth middleware for authentication, add UserProfile SQLModel table for profile storage, create `/personalize` and `/translate` API endpoints leveraging OpenAI API with caching strategies, integrate authentication UI components in Docusaurus frontend using React, and implement chapter-level personalization/translation controls.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/React 19 (frontend), Node.js 20+ (Docusaurus)
**Primary Dependencies**: Better-Auth (authentication), FastAPI (backend API), SQLModel (ORM), Neon PostgreSQL (user data), OpenAI API (content personalization & translation), Docusaurus 3.9.2 (frontend)
**Storage**: Neon PostgreSQL (user profiles, personalized content cache, translation cache), existing Session/ChatHistory tables extended
**Testing**: pytest (backend unit/integration), React Testing Library (frontend components), manual end-to-end testing for hackathon judges
**Target Platform**: Web (Docusaurus static site + FastAPI backend), Docker containers for deployment
**Project Type**: Web application (frontend: Docusaurus + backend: FastAPI)
**Performance Goals**:
  - Authentication: <1s login/signup response time
  - Personalization: <10s for chapter content rewriting (3000 words)
  - Translation: <2s for cached translations, <15s for uncached
  - Cache hit rate: >90% for translations
**Constraints**:
  - Must not break existing RAG chatbot functionality
  - Must integrate with existing Neon database schema
  - Better-Auth must provide persistent sessions (cookie-based or JWT)
  - OpenAI API rate limits (3 RPM for gpt-4, 60 RPM for gpt-3.5-turbo)
**Scale/Scope**:
  - Expected users: 50-100 hackathon judges + demo audience
  - Content volume: 8 chapters (~20,000 words total)
  - Translation cache: ~8 chapters × 3 difficulty levels = 24 personalized versions + 8 Urdu translations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Constitutional Alignment

1. **Principle I: Grounded Retrieval (RAG-First Architecture)** - ✅ Compliant
   - Personalization feature still uses original book content as source; OpenAI only adjusts presentation complexity, not content accuracy
   - Translation preserves technical grounding by translating existing content without generation
   - No impact to existing RAG chatbot citation requirements

2. **Principle II: Performance & Cost Efficiency** - ✅ Compliant with caching strategy
   - Translation caching reduces OpenAI API calls by 90%+ (per SC-010)
   - Personalized content caching considered (optional) to reduce costs
   - Performance targets met: <10s personalization, <2s cached translation
   - Use GPT-3.5-turbo for translations (lower cost), GPT-4 for complex personalization if needed

3. **Principle III: Data Integrity & Schema Consistency** - ✅ Compliant
   - New SQLModel tables: UserProfile, PersonalizedContent (optional), Translation
   - Foreign keys: UserProfile.user_id → User.id, Translation.chapter_id → Chapter.id
   - Better-Auth schema integrates with existing user management
   - All timestamps UTC ISO-8601, enums for user_level/background

4. **Principle IV: Security & Input Validation** - ✅ Compliant
   - Better-Auth handles password hashing, session management, CSRF protection
   - Pydantic models validate all API requests
   - Rate limiting applied to /personalize and /translate endpoints
   - CORS restricted to Docusaurus frontend origin

5. **Principle V: Clean Architecture & Minimal Dependencies** - ⚠️ Adding Better-Auth dependency
   - Better-Auth is additional dependency but necessary for bonus feature requirements
   - Alternative (manual JWT auth) would require more code and security risk
   - Better-Auth aligns with clean architecture via middleware pattern
   - **Justification**: Better-Auth provides production-grade authentication with <10 lines integration, reducing security risk vs. custom implementation

6. **Principle VI: Observability & Production Readiness** - ✅ Compliant
   - Health checks unaffected; auth endpoints include error logging
   - Graceful degradation: personalization/translation failures show original content
   - Error responses follow standard schema with request IDs

7. **Principle VII: Personalization & User Experience** - ✅ Core feature alignment
   - Extends existing `user_level` concept with profile-based background collection
   - Personalization system prompts adapt to Beginner/Intermediate/Advanced selections
   - Compatible with existing chat history retrieval

8. **Principle VIII: Multilingual Support (Urdu Translation)** - ✅ Core feature alignment
   - Implements constitution requirement for Urdu translation
   - Translation caching strategy matches constitutional guidance
   - `/translate` API route matches constitutional spec

9. **Principle IX: Hallucination Prevention & Guardrails** - ✅ Compliant
   - Personalization prompt includes guardrail: "Rewrite the following chapter content for {level} users. Preserve all technical accuracy and facts. Only adjust language complexity and explanation depth."
   - Translation preserves technical terms to maintain grounding
   - No risk of hallucination since both features operate on existing book content

10. **Principle X: Testing & Quality Assurance** - ✅ Compliant
    - Unit tests for authentication flow, profile storage, personalization/translation APIs
    - Integration tests for Better-Auth + SQLModel
    - End-to-end tests for judges: signup → login → personalize → translate
    - Manual testing checklist for hackathon demo

### ⚠️ Constitution Violations Requiring Justification

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Better-Auth dependency | Hackathon requirement explicitly specifies Better-Auth (https://www.better-auth.com/) for authentication (50-point bonus) | Manual JWT/session auth would require 300+ lines of security-critical code, increasing risk; Better-Auth provides production-ready auth in <10 lines with persistent sessions, CSRF protection, and standardized API |

## Project Structure

### Documentation (this feature)

```text
specs/002-hackathon-bonuses/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output: Better-Auth integration, personalization strategies
├── data-model.md        # Phase 1 output: User, UserProfile, PersonalizedContent, Translation schemas
├── quickstart.md        # Phase 1 output: Developer setup guide for bonus features
├── contracts/           # Phase 1 output: API contracts
│   ├── auth-api.yaml   # Authentication endpoints (signup, signin, signout)
│   ├── personalization-api.yaml  # Personalization endpoints
│   └── translation-api.yaml      # Translation endpoints
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (backend + frontend)
backend/
├── api/
│   ├── routes.py               # [EXTEND] Add /auth/*, /personalize, /translate routes
│   ├── dependencies.py         # [EXTEND] Add Better-Auth dependency injection
│   └── middleware/
│       └── better_auth.py      # [NEW] Better-Auth middleware integration
├── models/
│   ├── user.py                 # [NEW] Better-Auth User model (or extend existing Session model)
│   ├── user_profile.py         # [NEW] UserProfile SQLModel (background questions)
│   ├── personalized_content.py # [NEW] PersonalizedContent cache model (optional)
│   └── translation.py          # [NEW] Translation cache model
├── agents/
│   ├── personalization_agent.py # [NEW] OpenAI agent for chapter rewriting
│   └── translation_agent.py     # [NEW] OpenAI agent for Urdu translation
├── db/
│   ├── postgres.py             # [EXTEND] Add UserProfile, Translation table creation
│   └── migrations/
│       └── 002_add_bonus_features.py # [NEW] Alembic migration for new tables
├── utils/
│   └── auth.py                 # [NEW] Better-Auth configuration and helpers
└── requirements.txt            # [EXTEND] Add better-auth, additional OpenAI dependencies

frontend/ (Docusaurus root)
├── src/
│   ├── components/
│   │   ├── AuthWidget/          # [NEW] Signup/Signin UI component
│   │   │   ├── index.tsx
│   │   │   └── styles.module.css
│   │   ├── ChatbotWidget/       # [EXTEND] Show user auth state, personalization context
│   │   │   └── index.tsx
│   │   ├── ChapterControls/     # [NEW] Difficulty selector + Translate button
│   │   │   ├── index.tsx
│   │   │   └── styles.module.css
│   │   └── PersonalizedChapter/ # [NEW] Displays personalized/translated content
│   │       ├── index.tsx
│   │       └── styles.module.css
│   └── pages/
│       └── docs/                # [EXTEND] Inject ChapterControls into chapter pages
└── docusaurus.config.ts         # [EXTEND] Configure Better-Auth client, API base URL

# Docker deployment (optional for hackathon, recommended for production)
docker-compose.yml               # [EXTEND] Add auth service configuration if needed
```

**Structure Decision**: Web application structure selected because the project has both a Docusaurus frontend and FastAPI backend. Better-Auth operates primarily on the backend with frontend integration via session cookies or JWT tokens. New components are added to `src/components/` for authentication UI and chapter-level controls. Backend extends existing `/api/routes.py` with new endpoints for auth, personalization, and translation.

## Phase 0: Research & Technology Selection

See [research.md](./research.md) for detailed research findings.

### Key Research Areas

1. **Better-Auth Integration with FastAPI**
   - Better-Auth is primarily a Node.js/JavaScript library; need to research Python alternatives or API-based integration
   - **NEEDS CLARIFICATION**: Better-Auth official docs focus on Next.js/Node.js. Python integration requires either:
     - Option A: Use Better-Auth as a separate Node.js microservice with FastAPI proxying requests
     - Option B: Implement similar auth patterns in Python using FastAPI-native libraries (FastAPI-Users, python-jose)
     - **Research Task**: Evaluate Better-Auth Python compatibility and recommend implementation approach

2. **Personalization Strategy: Caching vs. On-Demand**
   - **Option A**: Cache personalized content in PersonalizedContent table (faster retrieval, higher storage cost)
   - **Option B**: Generate on-demand (slower, no storage cost, always up-to-date)
   - **Research Task**: Analyze tradeoffs and recommend caching strategy based on hackathon demo performance requirements

3. **Translation Caching Key Strategy**
   - Hash-based key (hash(original_text + target_lang)) vs. chapter_id-based key
   - **Research Task**: Determine optimal cache key structure for translation lookups

4. **OpenAI Prompt Engineering**
   - Personalization system prompts for Beginner/Intermediate/Advanced levels
   - Translation prompts preserving technical terminology
   - **Research Task**: Design and test optimal prompts for content quality

## Phase 1: Data Models & API Contracts

See [data-model.md](./data-model.md) for complete entity definitions and relationships.

See [contracts/](./contracts/) for OpenAPI specifications of all endpoints.

See [quickstart.md](./quickstart.md) for developer setup guide.

### Key Entities Summary

1. **User** (Better-Auth managed or SQLModel)
   - Attributes: id, email, password_hash, created_at, updated_at
   - Managed by Better-Auth authentication system

2. **UserProfile** (SQLModel)
   - Attributes: id, user_id (FK to User), software_background (enum: Beginner/Intermediate/Advanced), hardware_background (enum: None/Basic/Hands-on), python_familiarity (bool), ros_familiarity (bool), aiml_familiarity (bool), created_at
   - Relationships: Many-to-One with User
   - Validation: All enum fields required; at least one familiarity field must be set

3. **PersonalizedContent** (SQLModel, optional caching table)
   - Attributes: id, chapter_id (FK to Chapter), difficulty_level (enum: Beginner/Intermediate/Advanced), personalized_text (Text), created_at
   - Relationships: Many-to-One with Chapter
   - Validation: personalized_text max 50,000 characters; unique constraint on (chapter_id, difficulty_level)

4. **Translation** (SQLModel)
   - Attributes: id, chapter_id (FK to Chapter), language_code (str: 'ur'), original_text (Text), translated_text (Text), cached_at
   - Relationships: Many-to-One with Chapter
   - Validation: unique constraint on (chapter_id, language_code); cache TTL 30 days

### API Endpoints Summary

**Authentication**:
- `POST /auth/signup` - Create account with profile questions
- `POST /auth/signin` - Authenticate user
- `POST /auth/signout` - Terminate session
- `GET /auth/me` - Get current user profile

**Personalization**:
- `POST /personalize` - Request personalized chapter content
  - Request: `{"chapter_id": "uuid", "difficulty_level": "Beginner"}`
  - Response: `{"personalized_content": "...", "cached": true/false}`

**Translation**:
- `POST /translate` - Translate chapter to Urdu
  - Request: `{"chapter_id": "uuid", "target_lang": "ur"}`
  - Response: `{"original": "...", "translated": "...", "cached": true/false}`

## Phase 2: Implementation Tasks (Deferred to /sp.tasks)

Task breakdown will be generated by `/sp.tasks` command and written to [tasks.md](./tasks.md).

Expected task categories:
1. **Backend Setup**: Better-Auth integration, database migrations, new SQLModel tables
2. **API Development**: Authentication endpoints, personalization endpoint, translation endpoint
3. **Agent Development**: Personalization agent (OpenAI prompt), translation agent
4. **Frontend Development**: AuthWidget component, ChapterControls component, PersonalizedChapter display
5. **Integration**: Connect frontend to backend APIs, session management, error handling
6. **Testing**: Unit tests, integration tests, end-to-end hackathon judge testing
7. **Documentation**: API docs, judge testing guide, deployment instructions

## Architectural Decision Records (ADRs)

**Potential ADRs** (to be created if significant decisions are made during implementation):

1. **ADR-001: Better-Auth Integration Strategy**
   - **Decision**: [To be determined in research.md] Use Better-Auth as Node.js microservice OR implement FastAPI-native auth
   - **Context**: Hackathon requires Better-Auth, but it's JavaScript-focused; FastAPI is Python
   - **Consequences**: Impacts deployment complexity, authentication flow, session management
   - **Suggested command**: `/sp.adr better-auth-integration-strategy`

2. **ADR-002: Personalization Caching Strategy**
   - **Decision**: [To be determined in research.md] Cache personalized content vs. generate on-demand
   - **Context**: 24 possible cached versions (8 chapters × 3 levels) vs. on-demand generation speed
   - **Consequences**: Storage cost vs. API cost and performance tradeoffs
   - **Suggested command**: `/sp.adr personalization-caching-strategy`

## Risk Analysis & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Better-Auth incompatible with Python backend | Medium | High | Research alternative: FastAPI-Users library or Node.js microservice proxy |
| OpenAI API rate limits during hackathon demo | Medium | High | Pre-generate and cache all personalized/translated content for 8 chapters before demo |
| Personalization quality insufficient (not noticeably different between levels) | Medium | Medium | Test prompts extensively; include 3-5 example rewrites in research phase |
| Session persistence fails across browser restarts | Low | High | Test Better-Auth session management thoroughly; verify cookie persistence |
| Translation quality poor or loses technical meaning | Medium | Medium | Manual review of Urdu translations; preserve English technical terms in translation |
| Integration complexity delays delivery | Medium | High | Prioritize P1 (Auth) → P2 (Personalization) → P3 (Translation); deliver incrementally |

## Next Steps

1. ✅ **Complete Phase 0**: Generate `research.md` with Better-Auth integration strategy, personalization/translation prompt design, caching decisions
2. ⏳ **Complete Phase 1**: Generate `data-model.md`, `contracts/*.yaml`, `quickstart.md`
3. ⏳ **Run `/sp.tasks`**: Generate detailed implementation tasks in `tasks.md`
4. ⏳ **Implementation**: Execute tasks following TDD principles (red → green → refactor)
5. ⏳ **Testing**: Validate all success criteria (SC-001 through SC-010) from spec.md
6. ⏳ **Demo Preparation**: Pre-cache content, prepare judge testing guide

---

**Status**: Phase 0 (Research) in progress. Phase 1 (Design) pending. Implementation tasks pending `/sp.tasks` command.
