"""
Personalization Agent - OpenAI Integration for Content Adaptation

Implements Phase 4 (US2): Personalized Chapter Content
Adapts book content to Beginner/Intermediate/Advanced difficulty levels.
"""

from typing import Optional, Literal
from openai import AsyncOpenAI
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Difficulty level type
DifficultyLevel = Literal["Beginner", "Intermediate", "Advanced"]

# Prompts for each difficulty level with hallucination guardrails
BEGINNER_PROMPT = """You are an expert educator adapting technical content for beginners.

TASK: Adapt the following robotics content for BEGINNER level readers.

RULES (CRITICAL - PREVENT HALLUCINATION):
1. PRESERVE FACTS: Do not add new facts, examples, or technical details not in the original
2. SIMPLIFY ONLY: Only simplify language, add analogies, and explain jargon using the original content
3. NO EXPANSION: Do not expand with external knowledge or additional concepts
4. STRUCTURE: Keep the same structure and key points as the original
5. ANALOGIES: Use everyday analogies to explain complex concepts (e.g., "like a bicycle chain" for mechanical linkages)
6. JARGON: Define technical terms in simple language inline (e.g., "actuators (motors that create movement)")

TARGET AUDIENCE: Software developers new to robotics, minimal hardware background

ADAPTATION STRATEGY:
- Replace technical jargon with plain language explanations
- Add brief analogies for complex mechanisms
- Break down dense paragraphs into smaller, digestible chunks
- Use "in other words" or "think of it as" for clarification
- Keep all original facts, numbers, and key concepts intact

Original content:
{content}

Provide the beginner-friendly adapted version:"""

INTERMEDIATE_PROMPT = """You are an expert educator adapting technical content for intermediate learners.

TASK: Adapt the following robotics content for INTERMEDIATE level readers.

RULES (CRITICAL - PREVENT HALLUCINATION):
1. PRESERVE FACTS: Do not add new facts, examples, or technical details not in the original
2. BALANCE: Maintain technical accuracy while adding practical context
3. NO EXPANSION: Do not expand with external knowledge or additional concepts
4. STRUCTURE: Keep the same structure and key points as the original
5. CONTEXT: Add brief practical context for concepts (e.g., "commonly used in industrial robots")
6. CONNECTIONS: Highlight relationships between concepts explicitly

TARGET AUDIENCE: Developers with some robotics exposure, basic hardware understanding

ADAPTATION STRATEGY:
- Keep technical terms but ensure they're clear
- Add brief "why this matters" context for key concepts
- Make implicit connections explicit (e.g., "This relates to X mentioned earlier")
- Maintain professional tone with moderate technical depth
- Keep all original facts, numbers, and key concepts intact

Original content:
{content}

Provide the intermediate-level adapted version:"""

ADVANCED_PROMPT = """You are an expert educator adapting technical content for advanced practitioners.

TASK: Adapt the following robotics content for ADVANCED level readers.

RULES (CRITICAL - PREVENT HALLUCINATION):
1. PRESERVE FACTS: Do not add new facts, examples, or technical details not in the original
2. CONDENSE: Make content more dense and technically precise
3. NO EXPANSION: Do not expand with external knowledge or additional concepts
4. STRUCTURE: May reorganize for logical flow, but keep all original points
5. PRECISION: Use precise technical terminology without simplification
6. IMPLICATIONS: Highlight technical implications and trade-offs from the original content

TARGET AUDIENCE: Experienced robotics engineers and AI practitioners

ADAPTATION STRATEGY:
- Remove explanatory scaffolding and analogies
- Condense verbose explanations to technical essence
- Assume deep technical background (no need to explain basic terms)
- Front-load technical details and specifications
- Keep all original facts, numbers, and key concepts intact

Original content:
{content}

Provide the advanced-level adapted version:"""


class PersonalizationAgent:
    """
    Agent for personalizing chapter content based on user difficulty level.

    Uses OpenAI GPT-3.5-turbo to adapt content to Beginner/Intermediate/Advanced levels.
    Implements strict hallucination guardrails to prevent adding external information.
    """

    def __init__(self):
        """Initialize personalization agent with async OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-3.5-turbo"  # Fast and cost-effective for text transformation

        self.prompts = {
            "Beginner": BEGINNER_PROMPT,
            "Intermediate": INTERMEDIATE_PROMPT,
            "Advanced": ADVANCED_PROMPT,
        }

        logger.info(f"PersonalizationAgent initialized with model: {self.model}")

    async def personalize_content(
        self,
        content: str,
        difficulty_level: DifficultyLevel,
    ) -> Optional[str]:
        """
        Personalize content for specified difficulty level.

        Args:
            content: Original chapter content to adapt
            difficulty_level: Target difficulty level (Beginner/Intermediate/Advanced)

        Returns:
            Personalized content string, or None if personalization fails

        Raises:
            Exception: If OpenAI API call fails
        """
        if difficulty_level not in self.prompts:
            logger.error(f"Invalid difficulty level: {difficulty_level}")
            return None

        logger.info(f"Personalizing content for {difficulty_level} level ({len(content)} chars)")

        try:
            # Get appropriate prompt for difficulty level
            prompt_template = self.prompts[difficulty_level]
            prompt = prompt_template.format(content=content)

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical educator specializing in adapting content to different skill levels while maintaining factual accuracy."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Low temperature for consistent, faithful adaptation
                max_tokens=2000,  # Sufficient for chapter content
            )

            personalized_text = response.choices[0].message.content.strip()

            logger.info(f"Successfully personalized content ({len(personalized_text)} chars)")

            return personalized_text

        except Exception as e:
            logger.error(f"Personalization failed for {difficulty_level} level: {e}", exc_info=True)
            return None


# Global agent instance (singleton pattern)
_personalization_agent_instance = None


def get_personalization_agent() -> PersonalizationAgent:
    """
    Get global PersonalizationAgent instance (singleton).

    Returns:
        PersonalizationAgent: Configured agent instance
    """
    global _personalization_agent_instance

    if _personalization_agent_instance is None:
        _personalization_agent_instance = PersonalizationAgent()

    return _personalization_agent_instance
