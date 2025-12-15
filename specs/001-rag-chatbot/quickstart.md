# RAG Chatbot Quickstart Guide

**Goal**: Get the RAG chatbot running locally in < 15 minutes

**Prerequisites**: Python 3.11+, Docker, Docker Compose, OpenAI API key

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Environment Setup](#2-environment-setup)
3. [Database Initialization](#3-database-initialization)
4. [Book Ingestion](#4-book-ingestion)
5. [Testing the Chatbot](#5-testing-the-chatbot)
6. [Running Tests](#6-running-tests)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Docker**: 20.10+ with Docker Compose
- **RAM**: Minimum 4GB (8GB recommended for local embeddings)
- **Disk**: 2GB free space for Docker volumes
- **OS**: Linux, macOS, or Windows with WSL2

### API Keys

- **OpenAI API Key**: Required for embeddings and answer generation
  - Sign up at https://platform.openai.com/
  - Ensure you have credits ($5-10 recommended for initial testing)
  - Alternative: Use `EMBEDDING_MODEL=local` for free local embeddings (MiniLM)

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.11+

# Check Docker
docker --version
docker-compose --version

# Check OpenAI API key (optional: test in Python)
python -c "import openai; print('OpenAI SDK installed')"
```

---

## 2. Environment Setup

### Step 2.1: Clone Repository (if not already done)

```bash
cd /path/to/dacu-sikki
```

### Step 2.2: Create Environment File

Copy the example environment file and fill in your secrets:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your configuration:

```bash
# backend/.env
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/rag_chatbot

# Vector Database
QDRANT_URL=http://qdrant:6333

# OpenAI API
OPENAI_API_KEY=sk-your-api-key-here  # <-- REPLACE WITH YOUR KEY

# Embedding Model (openai or local)
EMBEDDING_MODEL=openai

# Rate Limiting
REDIS_URL=memory://  # Use memory for local dev
RATE_LIMIT=20/minute

# Logging
LOG_LEVEL=INFO

# Optional: Book path
BOOK_PATH=/app/data/book_source/physical_ai_robotics.md
```

**Important**:

- Replace `sk-your-api-key-here` with your actual OpenAI API key
- Use `EMBEDDING_MODEL=local` if you want free local embeddings (slightly lower accuracy)
- `.env` is gitignored - never commit API keys to version control

### Step 2.3: Add Sample Book Content

Create a sample book file for testing (or use your actual book):

```bash
mkdir -p backend/data/book_source
cat > backend/data/book_source/physical_ai_robotics.md <<'EOF'
# Physical AI & Humanoid Robotics Essentials

## Chapter 1: Introduction to Physical AI

Physical AI combines artificial intelligence with physical embodiment in robots...

## Chapter 2: Sensing Systems

### 2.1 Vision Systems
Cameras and depth sensors enable robots to perceive their environment...

### 2.2 Force Sensors
Force-torque sensors measure interaction forces for safe manipulation...

## Chapter 3: Actuation Systems

### 3.1 Overview
Actuators convert electrical energy into mechanical motion...

### 3.2 Hydraulic Actuators
Hydraulic actuators provide high force density and are commonly used in heavy-duty robotic applications. They offer superior power-to-weight ratios compared to electric motors for large-scale systems.

### 3.3 Electric Actuators
Electric actuators use electric motors (DC, AC, or stepper) to produce mechanical motion. They are precise, easy to control, and widely used in industrial robots.

## Chapter 4: Control Systems

Control algorithms ensure robots execute desired motions accurately...

EOF
```

**Note**: For production, replace this with the actual "Physical AI & Humanoid Robotics Essentials" book content.

---

## 3. Database Initialization

### Step 3.1: Start Services with Docker Compose

From the repository root:

```bash
docker-compose up -d
```

This starts:
- **PostgreSQL**: Port 5432 (database for chat history, sessions)
- **Qdrant**: Port 6333 (vector database for embeddings)
- **FastAPI App**: Port 8000 (chatbot API)

**Verify services are running**:

```bash
docker-compose ps

# Expected output:
# NAME                IMAGE                 STATUS
# backend-app         rag-chatbot:latest    Up
# backend-postgres    postgres:15           Up
# backend-qdrant      qdrant/qdrant:latest  Up
```

### Step 3.2: Run Database Migrations

Initialize PostgreSQL schema with Alembic:

```bash
docker-compose exec app alembic upgrade head
```

**Expected output**:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial_schema
```

### Step 3.3: Verify Database Connection

```bash
# Check PostgreSQL connection
docker-compose exec postgres psql -U user -d rag_chatbot -c "\dt"

# Expected output: List of tables (sessions, chat_history, chapters, paragraphs)
```

```bash
# Check Qdrant connection
curl http://localhost:6333/collections

# Expected output: {"result": {"collections": []}}  (empty initially)
```

---

## 4. Book Ingestion

### Step 4.1: Load Book Content

Use the admin endpoint to process and embed the book:

```bash
curl -X POST http://localhost:8000/admin/load_book \
  -H "Content-Type: application/json" \
  -d '{
    "book_path": "/app/data/book_source/physical_ai_robotics.md",
    "chunk_size": 512,
    "overlap": 50,
    "embedding_model": "openai"
  }'
```

**Expected output** (takes 2-5 minutes for sample book):
```json
{
  "status": "success",
  "chunks_created": 8,
  "qdrant_upserted": 8,
  "chapters_processed": 4,
  "processing_time_seconds": 12,
  "embedding_model_used": "openai",
  "message": "Book successfully loaded into knowledge base"
}
```

**Troubleshooting**:
- If you see `"OpenAI API error"`, check your API key in `.env`
- If you see `"Qdrant connection failed"`, ensure Qdrant is running (`docker-compose ps`)
- For free local embeddings, use `"embedding_model": "local"` (no API key required)

### Step 4.2: Verify Ingestion

Check that chunks were created:

```bash
# Check PostgreSQL paragraphs
docker-compose exec postgres psql -U user -d rag_chatbot -c "SELECT COUNT(*) FROM paragraphs;"

# Check Qdrant collection
curl http://localhost:6333/collections/physical_ai_robotics_book

# Expected: Collection with 8 points (vectors)
```

---

## 5. Testing the Chatbot

### Step 5.1: Ask a Question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are hydraulic actuators used for in robotics?"
  }'
```

**Expected output**:
```json
{
  "answer": "Hydraulic actuators are used in robotics for heavy-duty applications requiring high force density. They provide superior power-to-weight ratios compared to electric motors in large-scale systems.",
  "citations": [
    {
      "chapter": "Chapter 3: Actuation Systems",
      "section": "3.2 Hydraulic Actuators",
      "paragraph": 0
    }
  ],
  "query_id": "660e8400-e29b-41d4-a716-446655440000",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "processing_time_ms": 1850
}
```

**Note**: Save the `session_id` for follow-up questions.

### Step 5.2: Ask a Follow-Up Question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "What about electric actuators?"
  }'
```

**Expected**: Answer about electric actuators with citations.

### Step 5.3: Retrieve Conversation History

```bash
curl http://localhost:8000/history/550e8400-e29b-41d4-a716-446655440000
```

**Expected**: JSON array with all Q&A pairs from the session.

### Step 5.4: Clear Conversation

```bash
curl -X DELETE http://localhost:8000/history/550e8400-e29b-41d4-a716-446655440000
```

**Expected**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "deleted_count": 2,
  "message": "Conversation history cleared successfully"
}
```

### Step 5.5: Health Check

```bash
curl http://localhost:8000/health
```

**Expected**:
```json
{
  "status": "healthy",
  "services": {
    "postgres": true,
    "qdrant": true,
    "openai_api": true
  },
  "version": "1.0.0",
  "uptime_seconds": 3600
}
```

---

## 6. Running Tests

### Step 6.1: Run Unit Tests

```bash
docker-compose exec app pytest backend/tests/unit -v
```

**Expected**: All tests pass (covering embedder, retriever, chunker, reranker).

### Step 6.2: Run Integration Tests

```bash
docker-compose exec app pytest backend/tests/integration -v
```

**Expected**: All tests pass (covering API routes, RAG pipeline).

### Step 6.3: Run End-to-End Tests

```bash
docker-compose exec app pytest backend/tests/e2e -v
```

**Expected**: Full pipeline test (query → retrieval → answer).

### Step 6.4: Check Test Coverage

```bash
docker-compose exec app pytest --cov=backend --cov-report=html
```

**Expected**: Coverage report in `htmlcov/index.html` (target: 80%+).

---

## 7. Troubleshooting

### Common Issues

#### Issue 1: "OpenAI API key not found"

**Symptom**: `/chat` returns `500 Internal Server Error` with `"OpenAIAPIError"`

**Solution**:
1. Check `.env` file: `cat backend/.env | grep OPENAI_API_KEY`
2. Ensure key starts with `sk-`
3. Restart containers: `docker-compose restart`
4. Alternative: Use local embeddings (`EMBEDDING_MODEL=local`)

---

#### Issue 2: "Qdrant connection failed"

**Symptom**: Book ingestion fails with `"service_unavailable"`

**Solution**:
1. Check Qdrant is running: `docker-compose ps qdrant`
2. Check logs: `docker-compose logs qdrant`
3. Restart Qdrant: `docker-compose restart qdrant`
4. Verify connection: `curl http://localhost:6333/collections`

---

#### Issue 3: "PostgreSQL connection timeout"

**Symptom**: App fails to start or `/chat` returns database errors

**Solution**:
1. Check PostgreSQL is running: `docker-compose ps postgres`
2. Check logs: `docker-compose logs postgres`
3. Verify connection string in `.env`: `DATABASE_URL=postgresql://user:password@postgres:5432/rag_chatbot`
4. Reset database: `docker-compose down -v` then `docker-compose up -d`

---

#### Issue 4: "Rate limit exceeded" (429 error)

**Symptom**: After 20 requests, `/chat` returns `429 Too Many Requests`

**Solution**:
1. Wait 60 seconds for rate limit to reset
2. Increase limit in `.env`: `RATE_LIMIT=60/minute` (development only)
3. Use different IP or session to test

---

#### Issue 5: "No answer found" for valid questions

**Symptom**: Chatbot returns fallback message for questions that should be answerable

**Solution**:
1. Check book was ingested: `curl http://localhost:6333/collections/physical_ai_robotics_book`
2. Verify chunk count matches expected: `docker-compose exec postgres psql -U user -d rag_chatbot -c "SELECT COUNT(*) FROM paragraphs;"`
3. Test retrieval directly: `curl http://localhost:6333/collections/physical_ai_robotics_book/points/search -d '{"vector": [0.1, 0.2, ...], "limit": 5}'`
4. Re-ingest book with `force_reload: true`

---

#### Issue 6: "Docker out of memory"

**Symptom**: Containers crash or become unresponsive

**Solution**:
1. Increase Docker memory: Docker Desktop → Settings → Resources → Memory (8GB recommended)
2. Use local embeddings (lower memory): `EMBEDDING_MODEL=local`
3. Reduce chunk size: `"chunk_size": 256` (faster, less memory)

---

### Getting Help

- **Logs**: View service logs with `docker-compose logs -f <service>`
  - `docker-compose logs -f app` (FastAPI logs)
  - `docker-compose logs -f postgres` (Database logs)
  - `docker-compose logs -f qdrant` (Vector DB logs)

- **Interactive Shell**: Access containers for debugging
  - `docker-compose exec app bash` (App container)
  - `docker-compose exec postgres psql -U user -d rag_chatbot` (Database)

- **Check Environment**: Verify environment variables are loaded
  - `docker-compose exec app env | grep OPENAI_API_KEY`

---

## Next Steps

After quickstart completion:

1. **Customize Book Content**: Replace sample content with full book in `backend/data/book_source/`
2. **Frontend Integration**: Connect existing Docusaurus site to `/chat` endpoint
3. **Production Deployment**: See `research.md` for Cloud Run/ECS deployment guide
4. **Add Features**: Implement user personalization, Urdu translation (see constitution.md)
5. **Monitoring**: Set up logging, metrics, and alerting for production

---

## Useful Commands Cheat Sheet

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a service
docker-compose restart app

# View logs
docker-compose logs -f app

# Run tests
docker-compose exec app pytest -v

# Access database
docker-compose exec postgres psql -U user -d rag_chatbot

# Check Qdrant collections
curl http://localhost:6333/collections

# Health check
curl http://localhost:8000/health

# Submit a query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Your question here"}'

# Get history
curl http://localhost:8000/history/{session_id}

# Clear history
curl -X DELETE http://localhost:8000/history/{session_id}

# Reload book content
curl -X POST http://localhost:8000/admin/load_book \
  -H "Content-Type: application/json" \
  -d '{"book_path": "/app/data/book_source/physical_ai_robotics.md", "force_reload": true}'
```

---

**Congratulations! Your RAG chatbot is now running locally. 🎉**

**Estimated Time**: 10-15 minutes (excluding book ingestion)

For implementation details, see:
- **Data Models**: `data-model.md`
- **API Contracts**: `contracts/` directory
- **Research Decisions**: `research.md`
- **Architecture Plan**: `plan.md`
