#!/usr/bin/env python3
"""
RAG Chatbot Test Script

Quick test script to verify the RAG chatbot is working correctly.
Run this after starting the Docker services.

Usage:
    python test_chatbot.py
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
BOOK_PATH = "/app/data/book_source/physical_ai_robotics.md"

# ANSI color codes for pretty output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{title:^80}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")


def print_success(message: str):
    """Print a success message."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message: str):
    """Print an error message."""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message: str):
    """Print an info message."""
    print(f"{YELLOW}ℹ {message}{RESET}")


def test_health_check() -> bool:
    """Test if the API is running."""
    print_section("Step 1: Health Check")

    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print_success(f"API is running: {data.get('service', 'Unknown')}")
            print_info(f"Version: {data.get('version', 'Unknown')}")
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Is the server running?")
        print_info("Start the server with: docker compose up -d")
        return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False


def load_book() -> bool:
    """Load book content into the knowledge base."""
    print_section("Step 2: Load Book Content")

    print_info("This may take 5-10 minutes for full book processing...")
    print_info("Processing: Chunk → Embed → Store in Qdrant + PostgreSQL")

    payload = {
        "book_path": BOOK_PATH,
        "chunk_size": 512,
        "overlap": 50,
        "embedding_model": "openai"  # Change to "local" if you don't have OpenAI API key
    }

    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/admin/load_book",
            json=payload,
            timeout=600  # 10 minute timeout for book processing
        )

        if response.status_code == 200:
            data = response.json()
            elapsed = time.time() - start_time

            print_success("Book loaded successfully!")
            print(f"  • Chapters processed: {data['chapters_processed']}")
            print(f"  • Chunks created: {data['chunks_created']}")
            print(f"  • Qdrant vectors: {data['qdrant_upserted']}")
            print(f"  • Embedding model: {data['embedding_model_used']}")
            print(f"  • Processing time: {elapsed:.1f}s")
            return True
        elif response.status_code == 400:
            error = response.json()
            print_error(f"Invalid request: {error.get('detail', 'Unknown error')}")
            return False
        else:
            print_error(f"Load failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print_error("Request timed out. Book processing may still be running.")
        return False
    except Exception as e:
        print_error(f"Load book error: {e}")
        return False


def test_chat(query: str) -> Dict[str, Any]:
    """Test chatbot with a query."""
    payload = {
        "query": query
    }

    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=30
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "data": data,
                "elapsed": elapsed
            }
        else:
            return {
                "success": False,
                "error": response.text,
                "status_code": response.status_code
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def test_chatbot_queries():
    """Test chatbot with multiple queries."""
    print_section("Step 3: Test Chatbot Queries")

    test_queries = [
        {
            "query": "What are hydraulic actuators?",
            "description": "In-scope question (should return answer with citations)"
        },
        {
            "query": "What are the main types of sensors used in robotics?",
            "description": "In-scope question (should return answer with citations)"
        },
        {
            "query": "What's the weather like today?",
            "description": "Out-of-scope question (should return fallback response)"
        }
    ]

    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{YELLOW}Test {i}: {test_case['description']}{RESET}")
        print(f"Query: \"{test_case['query']}\"")
        print("-" * 80)

        result = test_chat(test_case['query'])

        if result['success']:
            data = result['data']

            print_success(f"Response received in {result['elapsed']:.2f}s")
            print(f"\n{GREEN}Answer:{RESET}")
            print(f"{data['answer']}\n")

            if data['citations']:
                print(f"{GREEN}Citations ({len(data['citations'])}):${RESET}")
                for j, citation in enumerate(data['citations'][:3], 1):  # Show first 3
                    print(f"  {j}. {citation.get('chapter', 'Unknown chapter')}")
                    if citation.get('section'):
                        print(f"     Section: {citation['section']}")
            else:
                print_info("No citations (fallback response)")

            print(f"\nMetadata:")
            print(f"  • Session ID: {data['session_id']}")
            print(f"  • Query ID: {data['query_id']}")
            print(f"  • Processing time: {data['processing_time_ms']}ms")

        else:
            print_error(f"Query failed: {result.get('error', 'Unknown error')}")


def main():
    """Main test execution."""
    print(f"\n{BLUE}{'*' * 80}{RESET}")
    print(f"{BLUE}{'RAG Chatbot Test Suite':^80}{RESET}")
    print(f"{BLUE}{'*' * 80}{RESET}")

    # Step 1: Health check
    if not test_health_check():
        print_error("\n❌ Health check failed. Cannot proceed with tests.")
        print_info("Make sure the API server is running:")
        print_info("  1. Start services: docker compose up -d")
        print_info("  2. Wait for services to be ready (~30s)")
        print_info("  3. Run this script again")
        return

    # Step 2: Load book (optional - comment out if already loaded)
    print_info("\nDo you want to load the book? (This takes 5-10 minutes)")
    print_info("Skip this if you've already loaded the book content.")
    user_input = input(f"{YELLOW}Load book? [y/N]: {RESET}").strip().lower()

    if user_input == 'y':
        if not load_book():
            print_error("\n❌ Book loading failed. Fix errors and try again.")
            return
    else:
        print_info("Skipping book load. Assuming book is already in knowledge base.")

    # Step 3: Test chatbot
    test_chatbot_queries()

    # Summary
    print_section("Test Summary")
    print_success("All tests completed!")
    print_info("\nNext steps:")
    print_info("  • Try your own questions via POST /chat")
    print_info("  • Check conversation history via GET /history/{session_id}")
    print_info("  • View API docs at http://localhost:8000/docs")


if __name__ == "__main__":
    main()
