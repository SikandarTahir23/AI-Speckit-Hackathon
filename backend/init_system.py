"""
System Initialization Script

This script:
1. Creates database tables
2. Loads book content into the RAG system
3. Verifies connections to Qdrant and PostgreSQL

Run this ONCE before starting the backend server.
"""

import sys
import os
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logger
from utils.config import settings
from db.postgres import create_db_and_tables, check_connection as check_postgres
from db.qdrant_client import check_connection as check_qdrant, create_collection, COLLECTION_OPENAI, COLLECTION_LOCAL
import requests

logger = setup_logger(__name__)


def main():
    """Initialize the RAG chatbot system"""

    print("\n" + "="*60)
    print("RAG CHATBOT SYSTEM INITIALIZATION")
    print("="*60 + "\n")

    # Step 1: Check PostgreSQL connection
    print("Step 1/5: Checking PostgreSQL connection...")
    if check_postgres():
        print("[OK] PostgreSQL connection successful\n")
    else:
        print("[ERROR] PostgreSQL connection failed!")
        print("Please check your DATABASE_URL in .env file")
        print("Expected format: postgresql://user:pass@host:port/dbname?sslmode=require")
        return False

    # Step 2: Check Qdrant connection
    print("Step 2/5: Checking Qdrant Cloud connection...")
    if check_qdrant():
        print("[OK] Qdrant Cloud connection successful\n")
    else:
        print("[ERROR] Qdrant connection failed!")
        print("Please check your QDRANT_URL and QDRANT_API_KEY in .env file")
        return False

    # Step 3: Create database tables
    print("Step 3/5: Creating database tables...")
    try:
        create_db_and_tables()
        print("[OK] Database tables created successfully\n")
    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
        return False

    # Step 4: Create Qdrant collection
    print("Step 4/5: Creating Qdrant collection...")
    try:
        collection_name = COLLECTION_OPENAI if settings.EMBEDDING_MODEL == "openai" else COLLECTION_LOCAL
        vector_size = 1536 if settings.EMBEDDING_MODEL == "openai" else 384
        create_collection(collection_name, vector_size)
        print(f"[OK] Qdrant collection '{collection_name}' ready\n")
    except Exception as e:
        print(f"[ERROR] Failed to create Qdrant collection: {e}")
        return False

    # Step 5: Load book content
    print("Step 5/5: Loading book content into RAG system...")
    print(f"   Book path: {settings.BOOK_PATH}")

    # Check if book file exists
    if not os.path.exists(settings.BOOK_PATH):
        print(f"[ERROR] Book file not found at: {settings.BOOK_PATH}")
        print("Please ensure the book markdown file exists at the specified path")
        return False

    try:
        # Load book via API endpoint
        print("   Starting book ingestion...")
        print("   This may take a few minutes as it generates embeddings for all content...")

        # Note: We need to start the server temporarily or call the function directly
        # For this script, we'll import and call the function directly
        from db.postgres import get_session
        from api.routes import load_book
        from pydantic import BaseModel

        # Create request
        class LoadBookRequest(BaseModel):
            book_path: str
            chunk_size: int = 512
            overlap: int = 50
            embedding_model: str = "openai"

        request = LoadBookRequest(
            book_path=settings.BOOK_PATH,
            embedding_model=settings.EMBEDDING_MODEL
        )

        # Get database session
        session_gen = get_session()
        session = next(session_gen)

        # Import the async function and run it
        import asyncio
        result = asyncio.run(load_book(request, session))

        print(f"\n[OK] Book loaded successfully!")
        print(f"   Chapters processed: {result.chapters_processed}")
        print(f"   Chunks created: {result.chunks_created}")
        print(f"   Vectors in Qdrant: {result.qdrant_upserted}")
        print(f"   Processing time: {result.processing_time_seconds}s")
        print(f"   Embedding model: {result.embedding_model_used}\n")

    except Exception as e:
        print(f"[ERROR] Failed to load book content: {e}")
        logger.error("Book loading error:", exc_info=True)
        return False

    # Success!
    print("\n" + "="*60)
    print("[SUCCESS] INITIALIZATION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("   1. Start the backend server:")
    print("      cd backend")
    print("      python main.py")
    print("\n   2. Start the frontend:")
    print("      npm start")
    print("\n   3. Open http://localhost:3000 and test the chatbot!")
    print("\n" + "="*60 + "\n")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Initialization interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        logger.error("Initialization failed:", exc_info=True)
        sys.exit(1)
