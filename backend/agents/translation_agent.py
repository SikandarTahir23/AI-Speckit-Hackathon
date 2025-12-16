"""
Translation Agent - Google Gemini Integration for Urdu Translation

Implements Phase 5 (US3): Urdu Translation
Translates book content to Urdu while preserving technical terms.
Uses Google Gemini API for fast, accurate translation.
"""

from typing import Optional
import google.generativeai as genai
from utils.config import settings
from utils.logger import setup_logger
import os

logger = setup_logger(__name__)

# Urdu translation prompt with technical term preservation rules
URDU_TRANSLATION_PROMPT = """You are an expert technical translator specializing in English to Urdu translation for robotics and AI content.

TASK: Translate the following English text to Urdu using URDU SCRIPT (اردو رسم الخط). You MUST write the output in Urdu/Arabic script, NOT in English or romanized text.

CRITICAL RULES (PREVENT MISTRANSLATION):
1. OUTPUT IN URDU SCRIPT: Write your entire translation in Urdu script (اردو). Do NOT use Latin/English characters except for preserved technical terms.
2. PRESERVE TECHNICAL TERMS: Keep English technical terms unchanged (e.g., "actuator", "kinematics", "sensor", "robot", "AI", "algorithm")
3. ACCURACY: Provide accurate, natural Urdu translation
4. NO ADDITIONS: Do not add explanations or content not in the original
5. FORMATTING: Preserve markdown formatting (headers, lists, code blocks)
6. READABILITY: Use clear, formal Urdu suitable for technical documentation
7. NUMBERS: Keep all numbers and measurements in English format
8. RIGHT-TO-LEFT: Remember Urdu is written right-to-left

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
- Translate descriptive text and explanations to Urdu IN URDU SCRIPT (اردو رسم الخط)
- Keep technical vocabulary in English
- Maintain paragraph structure
- Preserve all markdown syntax
- Use formal/academic Urdu style
- Write right-to-left as Urdu is read

Example of correct output format:
"Physical AI ایک ایسا نظام ہے جو مشینوں کو حقیقی دنیا میں intelligent طریقے سے کام کرنے کی اجازت دیتا ہے۔"

Original English content:
{content}

Provide the Urdu translation (MUST be in Urdu script اردو):"""


class TranslationAgent:
    """
    Agent for translating chapter content to Urdu.

    Uses Google Gemini API to translate content while preserving
    technical terms in English for clarity and consistency.
    """

    def __init__(self):
        """Initialize translation agent with Google Gemini."""
        gemini_api_key = os.getenv('GEMINI_API_KEY') or settings.GEMINI_API_KEY if hasattr(settings, 'GEMINI_API_KEY') else None

        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or settings")

        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')  # Gemini Flash Latest (better free tier quota)

        logger.info(f"TranslationAgent initialized with Gemini Flash Latest")

    async def translate_to_urdu(
        self,
        content: str,
    ) -> Optional[str]:
        """
        Translate content from English to Urdu using Google Gemini.

        Args:
            content: Original English chapter content to translate

        Returns:
            Urdu translated text, or None if translation fails

        Raises:
            Exception: If Gemini API call fails
        """
        logger.info(f"Translating content to Urdu with Gemini ({len(content)} chars)")

        try:
            # Format prompt with content
            prompt = URDU_TRANSLATION_PROMPT.format(content=content)

            # Call Gemini API (synchronous - Gemini SDK doesn't have async yet)
            import asyncio
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Low temperature for consistent translation
                    max_output_tokens=2500,
                )
            )

            translated_text = response.text.strip()

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
