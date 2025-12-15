"""
Qdrant Vector Database Client

Manages Qdrant connection, collection creation, and vector operations.
Implements data-model.md Qdrant Collection configuration.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional
from utils.config import settings
from utils.logger import setup_logger
import uuid
import time

logger = setup_logger(__name__)

# Collection names
COLLECTION_OPENAI = "physical_ai_robotics_book"  # OpenAI embeddings (1536 dims)
COLLECTION_LOCAL = "physical_ai_robotics_book_local"  # MiniLM embeddings (384 dims)


def get_qdrant_client() -> QdrantClient:
    """
    Get Qdrant client instance.

    Returns:
        QdrantClient: Connected Qdrant client
    """
    try:
        # Use API key if provided (required for Qdrant Cloud)
        if settings.QDRANT_API_KEY:
            client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY
            )
            logger.info(f"Connected to Qdrant Cloud at {settings.QDRANT_URL}")
        else:
            client = QdrantClient(url=settings.QDRANT_URL)
            logger.info(f"Connected to Qdrant (local) at {settings.QDRANT_URL}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        raise


def create_collection(collection_name: str, vector_size: int = 1536) -> bool:
    """
    Create Qdrant collection with specified configuration.

    Args:
        collection_name: Name of collection to create
        vector_size: Dimension of embedding vectors (1536 for OpenAI, 384 for MiniLM)

    Returns:
        bool: True if collection created or already exists
    """
    client = get_qdrant_client()

    try:
        # Check if collection already exists
        collections = client.get_collections().collections
        if any(col.name == collection_name for col in collections):
            logger.info(f"Collection '{collection_name}' already exists")
            return True

        # Create collection with HNSW index configuration
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,  # Cosine similarity for semantic search
            ),
            hnsw_config={
                "m": 16,  # Number of edges per node (balanced accuracy/memory)
                "ef_construct": 100,  # Construction time accuracy
            },
        )

        logger.info(
            f"Created collection '{collection_name}' with {vector_size} dimensions"
        )

        # Create payload index for chapter filtering
        client.create_payload_index(
            collection_name=collection_name,
            field_name="chapter_number",
            field_schema="integer",
        )

        logger.info(f"Created payload index on 'chapter_number' for '{collection_name}'")

        return True

    except Exception as e:
        logger.error(f"Failed to create collection '{collection_name}': {e}")
        raise


def upsert_points(
    collection_name: str,
    points: List[Dict],
) -> bool:
    """
    Upsert points (embeddings) into Qdrant collection.

    Args:
        collection_name: Target collection name
        points: List of point dictionaries with 'id', 'vector', and 'payload'

    Returns:
        bool: True if upsert successful

    Example point structure:
        {
            "id": "880e8400-e29b-41d4-a716-446655440000",
            "vector": [0.123, -0.456, ...],
            "payload": {
                "chunk_id": "770e8400-e29b-41d4-a716-446655440000",
                "chapter_number": 3,
                "chapter_title": "Actuation Systems",
                "paragraph_index": 5,
                "content": "Hydraulic actuators provide...",
                "section_name": "3.2 Hydraulic Actuators",
                "token_count": 487,
                "char_count": 1950,
            }
        }
    """
    client = get_qdrant_client()

    try:
        # Convert to PointStruct objects
        point_structs = [
            PointStruct(
                id=point["id"],
                vector=point["vector"],
                payload=point["payload"],
            )
            for point in points
        ]

        # Upsert with retry logic
        client.upsert(
            collection_name=collection_name,
            points=point_structs,
        )

        logger.info(f"Upserted {len(points)} points to collection '{collection_name}'")
        return True

    except Exception as e:
        logger.error(f"Failed to upsert points to '{collection_name}': {e}")
        raise


def search_vectors(
    collection_name: str,
    query_vector: List[float],
    top_k: int = 10,
    score_threshold: float = 0.7,
    chapter_filter: Optional[int] = None,
) -> List[Dict]:
    """
    Search for similar vectors in Qdrant collection.

    Args:
        collection_name: Target collection name
        query_vector: Query embedding vector
        top_k: Number of results to return
        score_threshold: Minimum similarity score (0.0 to 1.0)
        chapter_filter: Optional chapter number to filter results

    Returns:
        List of search results with scores and payloads
    """
    client = get_qdrant_client()

    try:
        # Build filter if chapter specified
        search_filter = None
        if chapter_filter is not None:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="chapter_number",
                        match=MatchValue(value=chapter_filter),
                    )
                ]
            )

        # Perform search
        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=search_filter,
        ).points

        # Format results
        formatted_results = [
            {
                "id": str(result.id),
                "score": result.score,
                "payload": result.payload,
            }
            for result in results
        ]

        logger.info(
            f"Found {len(formatted_results)} results in '{collection_name}' (threshold: {score_threshold})"
        )

        return formatted_results

    except Exception as e:
        logger.error(f"Search failed in '{collection_name}': {e}")
        raise


def batch_upsert_with_retry(
    collection_name: str,
    points: List[Dict],
    batch_size: int = 100,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> int:
    """
    Upsert points in batches with retry logic.

    Args:
        collection_name: Target collection name
        points: List of point dictionaries with 'id', 'vector', and 'payload'
        batch_size: Number of points per batch (default 100)
        max_retries: Maximum retry attempts per batch (default 3)
        retry_delay: Delay in seconds between retries (default 1.0)

    Returns:
        int: Total number of points successfully upserted

    Raises:
        Exception: If all retries fail for any batch
    """
    total_upserted = 0
    total_batches = (len(points) + batch_size - 1) // batch_size

    logger.info(
        f"Starting batch upsert: {len(points)} points in {total_batches} batches to '{collection_name}'"
    )

    for batch_idx in range(0, len(points), batch_size):
        batch = points[batch_idx : batch_idx + batch_size]
        batch_num = (batch_idx // batch_size) + 1

        for attempt in range(1, max_retries + 1):
            try:
                upsert_points(collection_name, batch)
                total_upserted += len(batch)
                logger.info(
                    f"Batch {batch_num}/{total_batches}: upserted {len(batch)} points (total: {total_upserted})"
                )
                break  # Success, move to next batch

            except Exception as e:
                if attempt < max_retries:
                    logger.warning(
                        f"Batch {batch_num}/{total_batches} failed (attempt {attempt}/{max_retries}): {e}"
                    )
                    logger.info(f"Retrying in {retry_delay}s...")
                    time.sleep(retry_delay * attempt)  # Exponential backoff
                else:
                    logger.error(
                        f"Batch {batch_num}/{total_batches} failed after {max_retries} attempts: {e}"
                    )
                    raise

    logger.info(
        f"Batch upsert completed: {total_upserted}/{len(points)} points upserted to '{collection_name}'"
    )

    return total_upserted


def check_connection() -> bool:
    """
    Health check for Qdrant connection.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        client = get_qdrant_client()
        collections = client.get_collections()
        logger.info(f"Qdrant health check passed. {len(collections.collections)} collections found.")
        return True
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        return False


# Initialize collections on module import
try:
    # Create OpenAI collection (1536 dims) if using OpenAI embeddings
    if settings.EMBEDDING_MODEL == "openai":
        create_collection(COLLECTION_OPENAI, vector_size=1536)
    # Create local collection (384 dims) if using MiniLM
    elif settings.EMBEDDING_MODEL == "local":
        create_collection(COLLECTION_LOCAL, vector_size=384)
except Exception as e:
    logger.warning(f"Failed to initialize Qdrant collections on startup: {e}")
    logger.warning("Collections will be created on first use")
