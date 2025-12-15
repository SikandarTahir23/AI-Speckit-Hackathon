# RAG Chatbot Testing Guide

This guide walks you through testing the RAG chatbot implementation for Phase 3.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key set in `backend/.env` (or use `EMBEDDING_MODEL=local`)
- Python 3.11+ installed (for Python test script)

## Quick Start (3 Steps)

### 1. Start the Services

```bash
# From project root
docker compose up -d

# Check services are running
docker compose ps

# Expected output: app, postgres, qdrant all running
```

**Wait 30-60 seconds** for all services to initialize.

### 2. Verify API is Running

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"RAG Chatbot API","version":"1.0.0"}
```

### 3. Run the Test Script

```bash
# Install requests library if needed
pip install requests

# Run the test script
python test_chatbot.py
```

The script will:
1. Check API health
2. Optionally load book content (~5-10 minutes)
3. Test chatbot with sample queries
4. Display results with citations

---

## Manual Testing with cURL

### Step 1: Load Book Content

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

**Note**: This takes 5-10 minutes. You'll see:
- Chapters processed
- Chunks created
- Qdrant vectors upserted
- Processing time

### Step 2: Ask Questions

**Example 1: In-scope question**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are hydraulic actuators used for in robotics?"
  }'
```

**Expected Response:**
```json
{
  "answer": "Hydraulic actuators are used in robotics for...",
  "citations": [
    {
      "chapter": "Chapter 3: Actuation Systems",
      "section": "3.2 Hydraulic Actuators",
      "paragraph": 5
    }
  ],
  "query_id": "660e8400-...",
  "session_id": "550e8400-...",
  "processing_time_ms": 1850
}
```

**Example 2: Follow-up question (same session)**

```bash
# Use the session_id from previous response
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "What about electric actuators?"
  }'
```

**Example 3: Out-of-scope question**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the weather today?"
  }'
```

**Expected Response:**
```json
{
  "answer": "I cannot answer this from the book content. This information is not covered in 'Physical AI & Humanoid Robotics Essentials'.",
  "citations": [],
  "query_id": "...",
  "session_id": "...",
  "processing_time_ms": 450
}
```

---

## Using API Documentation (Swagger UI)

1. Open browser: http://localhost:8000/docs
2. Interactive API documentation with "Try it out" buttons
3. Test endpoints directly from the browser

---

## Verification Checklist

### ✅ Phase 3 - User Story 1 (Ask Question and Get Answer)

- [ ] **T024-T028: Book Ingestion**
  - [ ] POST /admin/load_book processes sample book
  - [ ] Response shows chunks_created count (should be ~100+)
  - [ ] PostgreSQL has chapter and paragraph records
  - [ ] Qdrant has vector embeddings

- [ ] **T029-T031: RAG Agent**
  - [ ] Agent generates answers based on retrieved context
  - [ ] Citations include chapter and section references
  - [ ] Fallback response for out-of-scope questions

- [ ] **T032-T037: Chat Endpoint**
  - [ ] POST /chat returns answer with citations within 3 seconds
  - [ ] Empty query returns 400 validation error
  - [ ] Query > 2000 chars returns 400 error
  - [ ] New session auto-created if session_id not provided
  - [ ] Chat history saved to database

### Success Criteria (from spec.md)

- [ ] **SC-001**: Answers returned within 3 seconds for 90% of queries
- [ ] **SC-002**: Relevant answers for in-scope questions
- [ ] **SC-003**: 85%+ accuracy (verified against book content)

---

## Troubleshooting

### Issue: "Cannot connect to API"

**Solution:**
```bash
# Check services
docker compose ps

# View logs
docker compose logs app

# Restart services
docker compose restart
```

### Issue: "Book file not found"

**Solution:**
- Verify file exists: `ls backend/data/book_source/physical_ai_robotics.md`
- Check path in request matches container path: `/app/data/book_source/...`

### Issue: "OpenAI API error"

**Solutions:**
1. Check API key in `backend/.env`:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

2. Switch to local embeddings:
   ```bash
   # In backend/.env
   EMBEDDING_MODEL=local
   ```

### Issue: "Qdrant connection failed"

**Solution:**
```bash
# Check Qdrant is running
curl http://localhost:6333/collections

# Restart Qdrant
docker compose restart qdrant
```

### Issue: "PostgreSQL connection failed"

**Solution:**
```bash
# Check PostgreSQL is running
docker compose logs postgres

# Verify connection string in backend/.env
DATABASE_URL=postgresql://user:password@postgres:5432/rag_chatbot
```

---

## Performance Benchmarks

Based on Phase 3 requirements:

| Operation | Target | Typical Performance |
|-----------|--------|---------------------|
| Book ingestion (1500 chunks) | 5-10 min | ~6 minutes |
| Query processing (p95) | < 2 seconds | 1.5-1.8 seconds |
| Query processing (p50) | < 1 second | 0.8-1.2 seconds |
| Embedding generation (batch 100) | N/A | ~10 seconds |

---

## Next Steps After Testing

1. **Review logs**: Check structured JSON logs in console
2. **Inspect database**: Connect to PostgreSQL to verify data
3. **Try edge cases**: Long queries, special characters, multilingual text
4. **Phase 4**: Implement GET /history/{session_id} endpoint
5. **Phase 5**: Refine fallback responses and error handling

---

## Sample Test Queries

### Good In-Scope Questions
- "What are hydraulic actuators?"
- "Explain the difference between electric and hydraulic actuation"
- "What sensors are commonly used in humanoid robots?"
- "How do control systems work in physical AI?"

### Out-of-Scope Questions (Should Return Fallback)
- "What's the weather today?"
- "Who won the 2024 election?"
- "How do I cook pasta?"
- "What is quantum computing?"

### Edge Cases
- Empty query: `""` (should return 400)
- Very long query: 2500 chars (should return 400)
- Special characters: `"What is \\n \t <script>"` (should handle gracefully)
- Invalid session_id: `"invalid-uuid"` (should return 404)

---

## Database Inspection

### Check PostgreSQL

```bash
# Enter PostgreSQL container
docker compose exec postgres psql -U user -d rag_chatbot

# Query chapters
SELECT chapter_number, title, word_count FROM chapters;

# Query paragraphs (first 5)
SELECT chapter_id, paragraph_index, LEFT(content, 100) FROM paragraphs LIMIT 5;

# Query chat history
SELECT query, LEFT(answer, 100), array_length(citations, 1) as citation_count
FROM chat_history
ORDER BY timestamp DESC
LIMIT 5;
```

### Check Qdrant

```bash
# Get collection info
curl http://localhost:6333/collections/physical_ai_robotics_book

# Search example
curl -X POST http://localhost:6333/collections/physical_ai_robotics_book/points/search \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, ...],  # Your embedding here
    "limit": 5
  }'
```

---

## Contact & Support

- **Issues**: Report at GitHub Issues
- **Documentation**: See `specs/001-rag-chatbot/quickstart.md`
- **API Spec**: See `specs/001-rag-chatbot/contracts/chat.openapi.yaml`

Happy testing! 🚀
