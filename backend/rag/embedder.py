"""
Embedder - Dual Embedding Strategy

Generates text embeddings using OpenAI (primary) or sentence-transformers (fallback).
Implements research.md Task 3: Embedding Model Selection.
"""

from typing import List, Union
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from utils.config import settings
from utils.logger import setup_logger
import numpy as np

logger = setup_logger(__name__)


class Embedder:
    """
    Dual-strategy embedding generator.

    Uses OpenAI text-embedding-3-small (1536 dims) when available,
    falls back to MiniLM-L6-v2 (384 dims) for cost-free operation.
    """

    def __init__(self):
        """Initialize embedder based on configuration."""
        self.model_type = settings.EMBEDDING_MODEL

        if self.model_type == "openai":
            self._init_openai()
        elif self.model_type == "local":
            self._init_local()
        else:
            raise ValueError(
                f"Invalid EMBEDDING_MODEL: {self.model_type}. Must be 'openai' or 'local'"
            )

        logger.info(f"Embedder initialized with model type: {self.model_type}")

    def _init_openai(self):
        """Initialize OpenAI embedding client."""
        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model_name = "text-embedding-3-small"
            self.dimensions = 1536
            logger.info(f"OpenAI embedder ready: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI embedder: {e}")
            raise

    def _init_local(self):
        """Initialize local sentence-transformers model."""
        try:
            self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            self.dimensions = 384
            logger.info("Local embedder ready: all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Failed to initialize local embedder: {e}")
            raise

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            List[float]: Embedding vector
        """
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of input texts to embed

        Returns:
            List[List[float]]: List of embedding vectors

        Raises:
            ValueError: If texts list is empty
            Exception: If embedding generation fails
        """
        if not texts:
            raise ValueError("Cannot embed empty text list")

        try:
            if self.model_type == "openai":
                return self._embed_openai(texts)
            else:
                return self._embed_local(texts)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI API.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            # OpenAI API processes batches efficiently
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts,
            )

            # Extract embeddings in original order
            embeddings = [data.embedding for data in response.data]

            logger.info(
                f"Generated {len(embeddings)} OpenAI embeddings ({self.dimensions} dims)"
            )

            return embeddings

        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise

    def _embed_local(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using local sentence-transformers model.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            # sentence-transformers returns numpy arrays
            embeddings_np = self.model.encode(
                texts,
                batch_size=32,
                show_progress_bar=False,
                convert_to_numpy=True,
            )

            # Convert to list of lists
            embeddings = embeddings_np.tolist()

            logger.info(
                f"Generated {len(embeddings)} local embeddings ({self.dimensions} dims)"
            )

            return embeddings

        except Exception as e:
            logger.error(f"Local embedding failed: {e}")
            raise

    def get_dimensions(self) -> int:
        """
        Get the dimensionality of embeddings.

        Returns:
            int: Embedding vector size (1536 for OpenAI, 384 for local)
        """
        return self.dimensions

    def get_model_info(self) -> dict:
        """
        Get information about the current embedding model.

        Returns:
            dict: Model type, name, and dimensions
        """
        info = {
            "type": self.model_type,
            "dimensions": self.dimensions,
        }

        if self.model_type == "openai":
            info["model_name"] = self.model_name
            info["cost_per_1m_tokens"] = 0.02  # USD
        else:
            info["model_name"] = "all-MiniLM-L6-v2"
            info["cost_per_1m_tokens"] = 0.0  # Free

        return info


# Global embedder instance (singleton pattern)
_embedder_instance = None


def get_embedder() -> Embedder:
    """
    Get global embedder instance (singleton).

    Returns:
        Embedder: Configured embedder instance
    """
    global _embedder_instance

    if _embedder_instance is None:
        _embedder_instance = Embedder()

    return _embedder_instance
