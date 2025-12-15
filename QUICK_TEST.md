# Quick Test Reference Card

## 🚀 3-Minute Quick Start

```bash
# 1. Start services
docker compose up -d

# 2. Wait 30 seconds, then health check
curl http://localhost:8000/health

# 3. Run automated test
python test_chatbot.py
```

## 📋 Essential Commands

### Load Book (One-Time Setup)
```bash
curl -X POST http://localhost:8000/admin/load_book \
  -H "Content-Type: application/json" \
  -d '{"book_path":"/app/data/book_source/physical_ai_robotics.md","embedding_model":"openai"}'
```

### Ask Question
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What are hydraulic actuators?"}'
```

### Test Fallback
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the weather today?"}'
```

## 🔍 Quick Checks

| Check | Command | Expected |
|-------|---------|----------|
| API Running | `curl http://localhost:8000/health` | `{"status":"healthy"}` |
| Qdrant | `curl http://localhost:6333/collections` | Collection list |
| PostgreSQL | `docker compose exec postgres pg_isready` | `accepting connections` |
| Logs | `docker compose logs app --tail=50` | No errors |

## 📊 What to Look For

### ✅ Success Indicators
- Answer with citations (in-scope questions)
- Fallback message (out-of-scope questions)
- Processing time < 3000ms
- Session ID returned
- No errors in logs

### ❌ Common Issues
- "Connection refused" → Services not started
- "File not found" → Wrong book path
- "OpenAI error" → Check API key in .env
- "Empty citations" → Check book was loaded

## 🎯 Phase 3 Test Checklist

- [ ] Health check passes
- [ ] Book loads successfully (~5-10 min)
- [ ] In-scope question returns answer + citations
- [ ] Out-of-scope question returns fallback
- [ ] Empty query returns 400 error
- [ ] Long query (>2000 chars) returns 400
- [ ] Response time < 3 seconds
- [ ] Session auto-created
- [ ] Chat history saved to DB

## 🌐 Web Interface

**Swagger UI**: http://localhost:8000/docs
- Interactive API testing
- Schema documentation
- Try all endpoints

---

**Full Guide**: See `TESTING.md`
**Python Script**: Run `python test_chatbot.py`
