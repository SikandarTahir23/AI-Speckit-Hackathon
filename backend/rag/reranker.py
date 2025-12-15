"""
Reranker - Cross-Encoder Reranking

Reranks top-k results using cross-encoder model for improved relevance.
Implements research.md reranking strategy to select top-N from top-K.
"""

from typing import List, Dict, Optional
from sentence_transformers import CrossEncoder
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Reranker:
    """
    Cross-encoder reranker for RAG pipeline.

    Uses cross-encoder model to rerank retrieved chunks based on
    query-passage relevance scores. More accurate than vector similarity alone.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_n: int = None,
    ):
        """
        Initialize reranker with cross-encoder model.

        Args:
            model_name: HuggingFace cross-encoder model name
            top_n: Number of top results to return after reranking (default from settings: 5)
        """
        self.model_name = model_name
        self.top_n = top_n or settings.RERANK_TOP_N

        try:
            self.model = CrossEncoder(model_name)
            logger.info(f"Reranker initialized: {model_name}, top_n={self.top_n}")
        except Exception as e:
            logger.error(f"Failed to initialize reranker: {e}")
            raise

    def rerank(
        self,
        query: str,
        chunks: List[Dict],
        top_n: Optional[int] = None,
    ) -> List[Dict]:
        """
        Rerank retrieved chunks using cross-encoder.

        Args:
            query: User question text
            chunks: List of retrieved chunks from retriever
            top_n: Override default top_n for this query

        Returns:
            List of reranked chunks (top_n best matches) with updated scores

        Example return:
            [
                {
                    "id": "...",
                    "score": 0.87,  # Original vector similarity
                    "rerank_score": 0.95,  # Cross-encoder score
                    "content": "...",
                    ...
                },
                ...
            ]
        """
        if not chunks:
            logger.warning("No chunks provided for reranking")
            return []

        if not query or not query.strip():
            logger.warning("Empty query provided to reranker")
            return chunks

        # Use provided top_n or default
        n = top_n if top_n is not None else self.top_n

        try:
            # Prepare query-passage pairs for cross-encoder
            pairs = [[query, chunk["content"]] for chunk in chunks]

            # Get cross-encoder scores
            scores = self.model.predict(pairs)

            # Add rerank scores to chunks
            for chunk, score in zip(chunks, scores):
                chunk["rerank_score"] = float(score)

            # Sort by rerank score (descending)
            reranked = sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)

            # Return top-n
            top_reranked = reranked[:n]

            logger.info(
                f"Reranked {len(chunks)} chunks, returning top {len(top_reranked)} "
                f"(top rerank score: {top_reranked[0]['rerank_score']:.3f})"
            )

            return top_reranked

        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            # Fallback: return original chunks sorted by vector score
            logger.warning("Falling back to vector similarity ranking")
            return chunks[:n]

    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about the reranker model.

        Returns:
            dict: Model name and top_n configuration
        """
        return {
            "model_name": self.model_name,
            "top_n": self.top_n,
        }


# Global reranker instance (singleton pattern)
_reranker_instance = None


def get_reranker() -> Reranker:
    """
    Get global reranker instance (singleton).

    Returns:
        Reranker: Configured reranker instance
    """
    global _reranker_instance

    if _reranker_instance is None:
        _reranker_instance = Reranker()

    return _reranker_instance
