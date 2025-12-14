"""
Translation Agent - OpenAI Integration for Urdu Translation

Implements Phase 5 (US3): Urdu Translation
Translates book content to Urdu while preserving technical terms.
"""

from typing import Optional
from openai import AsyncOpenAI
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Urdu translation prompt with technical term preservation rules
URDU_TRANSLATION_PROMPT = """You are an expert technical translator specializing in English to Urdu translation for robotics and AI content.

TASK: Translate the following English text to Urdu.

CRITICAL RULES (PREVENT MISTRANSLATION):
1. PRESERVE TECHNICAL TERMS: Keep English technical terms unchanged (e.g., "actuator", "kinematics", "sensor", "robot", "AI", "algorithm")
2. ACCURACY: Provide accurate, natural Urdu translation
3. NO ADDITIONS: Do not add explanations or content not in the original
4. FORMATTING: Preserve markdown formatting (headers, lists, code blocks)
5. READABILITY: Use clear, formal Urdu suitable for technical documentation
6. NUMBERS: Keep all numbers and measurements in English format

TECHNICAL TERMS TO PRESERVE (keep in English):
- Robot, robotics, humanoid, physical AI
- Actuator, sensor, controller, motor
- Algorithm, model, neural network, machine learning
- ROS (Robot Operating System), simulation, digital twin
- Kinematics, dynamics, trajectory, control
- Vision, perception, manipulation, locomotion
- Python, code, API, framework, library
- Any programming terms or code snippets

TRANSLATION STRATEGY:
- Translate descriptive text and explanations to Urdu
- Keep technical vocabulary in English
- Maintain paragraph structure
- Preserve all markdown syntax
- Use formal/academic Urdu style

Original English content:
{content}

Provide the Urdu translation:"""


class TranslationAgent:
    """
    Agent for translating chapter content to Urdu.

    Uses OpenAI GPT-3.5-turbo to translate content while preserving
    technical terms in English for clarity and consistency.
    """

    def __init__(self):
        """Initialize translation agent with async OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-3.5-turbo"  # Fast and cost-effective for translation

        logger.info(f"TranslationAgent initialized with model: {self.model}")

    async def translate_to_urdu(
        self,
        content: str,
    ) -> Optional[str]:
        """
        Translate content from English to Urdu.

        Args:
            content: Original English chapter content to translate

        Returns:
            Urdu translated text, or None if translation fails

        Raises:
            Exception: If OpenAI API call fails
        """
        logger.info(f"Translating content to Urdu ({len(content)} chars)")

        try:
            # Format prompt with content
            prompt = URDU_TRANSLATION_PROMPT.format(content=content)

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical translator specializing in English to Urdu translation for AI and robotics documentation."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Low temperature for consistent, accurate translation
                max_tokens=2500,  # Sufficient for chapter content translation
            )

            translated_text = response.choices[0].message.content.strip()

            logger.info(f"Successfully translated content to Urdu ({len(translated_text)} chars)")

            return translated_text

        except Exception as e:
            logger.error(f"Translation to Urdu failed: {e}", exc_info=True)
            return None


# Global agent instance (singleton pattern)
_translation_agent_instance = None


def get_translation_agent() -> TranslationAgent:
    """
    Get global TranslationAgent instance (singleton).

    Returns:
        TranslationAgent: Configured agent instance
    """
    global _translation_agent_instance

    if _translation_agent_instance is None:
        _translation_agent_instance = TranslationAgent()

    return _translation_agent_instance
