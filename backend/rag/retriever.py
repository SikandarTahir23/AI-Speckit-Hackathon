"""
Retriever - Qdrant Vector Search

Searches Qdrant for relevant chunks using semantic similarity.
Implements retrieval with chapter filtering and metadata extraction.
"""

from typing import List, Dict, Optional
from db.qdrant_client import get_qdrant_client, search_vectors, COLLECTION_OPENAI, COLLECTION_LOCAL
from rag.embedder import get_embedder
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Retriever:
    """
    Vector search retriever for RAG pipeline.

    Queries Qdrant for semantically similar chunks based on query embeddings.
    Supports chapter filtering and configurable top-k and score thresholds.
    """

    def __init__(
        self,
        top_k: int = None,
        score_threshold: float = None,
    ):
        """
        Initialize retriever with configuration.

        Args:
            top_k: Number of results to retrieve (default from settings: 10)
            score_threshold: Minimum similarity score (default from settings: 0.7)
        """
        self.top_k = top_k or settings.RETRIEVAL_TOP_K
        self.score_threshold = score_threshold or settings.RETRIEVAL_SCORE_THRESHOLD
        self.embedder = get_embedder()

        # Determine collection based on embedding model
        if settings.EMBEDDING_MODEL == "openai":
            self.collection_name = COLLECTION_OPENAI
        else:
            self.collection_name = COLLECTION_LOCAL

        logger.info(
            f"Retriever initialized: top_k={self.top_k}, threshold={self.score_threshold}, collection={self.collection_name}"
        )

    def retrieve(
        self,
        query: str,
        chapter_filter: Optional[int] = None,
        top_k: Optional[int] = None,
    ) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: User question text
            chapter_filter: Optional chapter number to filter results
            top_k: Override default top_k for this query

        Returns:
            List of retrieved chunks with scores and metadata

        Example return:
            [
                {
                    "id": "880e8400-e29b-41d4-a716-446655440000",
                    "score": 0.87,
                    "content": "Hydraulic actuators provide high force density...",
                    "chapter_number": 3,
                    "chapter_title": "Actuation Systems",
                    "section_name": "3.2 Hydraulic Actuators",
                    "paragraph_index": 5,
                    "token_count": 487
                },
                ...
            ]
        """
        if not query or not query.strip():
            logger.warning("Empty query provided to retriever")
            return []

        # Use provided top_k or default
        k = top_k if top_k is not None else self.top_k

        try:
            # Generate query embedding
            query_vector = self.embedder.embed_text(query)

            # Search Qdrant
            results = search_vectors(
                collection_name=self.collection_name,
                query_vector=query_vector,
                top_k=k,
                score_threshold=self.score_threshold,
                chapter_filter=chapter_filter,
            )

            # Extract and format chunks
            chunks = []
            for result in results:
                payload = result["payload"]

                chunk = {
                    "id": result["id"],
                    "score": result["score"],
                    "content": payload.get("content", ""),
                    "chapter_number": payload.get("chapter_number"),
                    "chapter_title": payload.get("chapter_title", ""),
                    "section_name": payload.get("section_name", ""),
                    "paragraph_index": payload.get("paragraph_index", 0),
                    "token_count": payload.get("token_count", 0),
                    "chunk_id": payload.get("chunk_id", ""),
                }

                chunks.append(chunk)

            logger.info(
                f"Retrieved {len(chunks)} chunks for query (top score: {chunks[0]['score']:.3f})"
                if chunks
                else "No chunks retrieved (below threshold)"
            )

            return chunks

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            raise

    def check_confidence(self, chunks: List[Dict]) -> tuple[bool, float]:
        """
        Check if retrieval confidence is above threshold.

        Args:
            chunks: List of retrieved chunks with scores

        Returns:
            Tuple of (is_confident, top_score)
            - is_confident: True if top score >= threshold
            - top_score: Highest similarity score (0.0 if no chunks)
        """
        if not chunks:
            return False, 0.0

        top_score = chunks[0]["score"]
        is_confident = top_score >= self.score_threshold

        return is_confident, top_score

    def format_context(self, chunks: List[Dict], max_tokens: int = 2000) -> str:
        """
        Format retrieved chunks into context string for LLM.

        Args:
            chunks: List of retrieved chunks
            max_tokens: Maximum tokens for context (to fit in prompt)

        Returns:
            Formatted context string with chapter references
        """
        if not chunks:
            return ""

        context_parts = []
        total_tokens = 0

        for i, chunk in enumerate(chunks, 1):
            # Format: [Chapter X: Title - Section] content
            section_ref = f"[Chapter {chunk['chapter_number']}: {chunk['chapter_title']}"
            if chunk.get("section_name"):
                section_ref += f" - {chunk['section_name']}"
            section_ref += "]"

            chunk_text = f"{section_ref}\n{chunk['content']}\n"

            # Estimate tokens (rough approximation: 1 token ≈ 4 chars)
            chunk_tokens = len(chunk_text) // 4

            if total_tokens + chunk_tokens > max_tokens:
                logger.warning(
                    f"Context truncated at {i-1} chunks (reached {max_tokens} token limit)"
                )
                break

            context_parts.append(chunk_text)
            total_tokens += chunk_tokens

        context = "\n".join(context_parts)

        logger.info(
            f"Formatted context: {len(context_parts)} chunks, ~{total_tokens} tokens"
        )

        return context


# Global retriever instance (singleton pattern)
_retriever_instance = None


def get_retriever() -> Retriever:
    """
    Get global retriever instance (singleton).

    Returns:
        Retriever: Configured retriever instance
    """
    global _retriever_instance

    if _retriever_instance is None:
        _retriever_instance = Retriever()

    return _retriever_instance
