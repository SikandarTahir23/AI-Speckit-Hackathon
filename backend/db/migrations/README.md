# Database Migrations

This directory contains Alembic database migrations for the RAG chatbot.

## Initial Setup

```bash
# Navigate to backend directory
cd backend

# Create initial migration
alembic revision --autogenerate -m "Initial schema: sessions, chat_history, chapters, paragraphs"

# Apply migrations
alembic upgrade head
```

## Migration Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current migration version
alembic current

# Show migration history
alembic history
```

## Migration Versioning

- **Version 001**: Initial tables (sessions, chat_history, chapters, paragraphs)
- **Version 002**: Future - Add processing_time_ms, retrieval_score to ChatHistory
- **Version 003**: Future - Add user_level to Session for personalization

## Rollback Safety

All migrations must be reversible. Always test both `upgrade()` and `downgrade()` functions.
