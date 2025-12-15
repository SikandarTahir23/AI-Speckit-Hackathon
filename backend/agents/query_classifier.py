"""
Query Classifier - Determines Book-Relevance

Classifies queries as:
- IN_SCOPE: Related to book content (use RAG)
- OUT_OF_SCOPE: General question (use OpenAI fallback)
"""

from openai import OpenAI
from utils.config import settings
from utils.logger import setup_logger
from typing import Literal

logger = setup_logger(__name__)


class QueryClassifier:
    """
    Lightweight classifier to determine if query is book-related.

    Uses OpenAI with minimal context to avoid hallucination.
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"  # Fast, cheap model for classification

        self.classification_prompt = """You are a query classifier for a specialized chatbot about the book "Physical AI & Humanoid Robotics Essentials".

Your task: Determine if the user's question is RELATED to the book's topics or a GENERAL question.

**Book Topics Include:**
- Physical AI and embodied intelligence
- Humanoid robotics and robot design
- Actuators (hydraulic, electric, pneumatic)
- Sensors and perception systems
- Control systems and motion planning
- Robot kinematics and dynamics
- Human-robot interaction
- Robot learning and adaptation

**Classification Rules:**
- If the question is about ANY of the above topics → Return "IN_SCOPE"
- If the question is about weather, news, cooking, unrelated topics → Return "OUT_OF_SCOPE"
- If uncertain but mentions robotics/AI/sensors/actuators → Return "IN_SCOPE"

Respond with ONLY one word: "IN_SCOPE" or "OUT_OF_SCOPE"

User Question: {query}

Classification:"""

    def classify(self, query: str) -> Literal["IN_SCOPE", "OUT_OF_SCOPE"]:
        """
        Classify query as book-related or general.

        Args:
            query: User question

        Returns:
            "IN_SCOPE" if book-related, "OUT_OF_SCOPE" otherwise
        """
        try:
            prompt = self.classification_prompt.format(query=query)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,  # Deterministic
                max_tokens=10,  # Only need "IN_SCOPE" or "OUT_OF_SCOPE"
            )

            classification = response.choices[0].message.content.strip().upper()

            # Validate response
            if "IN_SCOPE" in classification or "IN-SCOPE" in classification:
                logger.info(f"Query classified as IN_SCOPE: {query[:50]}...")
                return "IN_SCOPE"
            else:
                logger.info(f"Query classified as OUT_OF_SCOPE: {query[:50]}...")
                return "OUT_OF_SCOPE"

        except Exception as e:
            logger.error(f"Classification failed: {e}. Defaulting to IN_SCOPE")
            # Fail-safe: try RAG first
            return "IN_SCOPE"


# Global classifier instance
_classifier_instance = None


def get_classifier() -> QueryClassifier:
    """Get global classifier instance (singleton)."""
    global _classifier_instance

    if _classifier_instance is None:
        _classifier_instance = QueryClassifier()

    return _classifier_instance
