"""
RAG Agent - OpenAI Agent SDK Configuration

Orchestrates the RAG pipeline using OpenAI's Agent SDK.
Implements plan.md Phase 3 (US1): RAG Agent Implementation.
"""

from typing import List, Dict, Optional
from openai import OpenAI
from utils.config import settings
from utils.logger import setup_logger
from rag.retriever import get_retriever
from rag.reranker import get_reranker

logger = setup_logger(__name__)


class RAGAgent:
    """
    RAG Agent for question answering with grounding.

    Uses OpenAI's Chat Completions API to generate answers based on
    retrieved context. Ensures all answers are grounded in source material
    or returns fallback response.
    """

    def __init__(self):
        """Initialize RAG agent with OpenAI client and system prompt."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL or "gpt-4o-mini"
        self.retriever = get_retriever()
        self.reranker = get_reranker()

        # System prompt for grounded answer generation
        self.system_prompt = """You are an expert AI assistant specialized in Physical AI and Humanoid Robotics.

Your task is to answer questions based ONLY on the provided context from the book "Physical AI & Humanoid Robotics Essentials".

CRITICAL RULES:
1. GROUNDING: Every answer MUST be grounded in the provided context. Never use external knowledge.
2. CITATIONS: Reference specific chapters, sections, and paragraphs when answering.
3. FALLBACK: If the context does not contain relevant information, respond with: "I cannot answer this from the book content. This information is not covered in 'Physical AI & Humanoid Robotics Essentials'."
4. ACCURACY: Do not hallucinate or make up information. Stick strictly to what's in the context.
5. CLARITY: Provide clear, concise answers that directly address the question.
6. FORMAT: Structure answers in natural language, referencing citations inline.

When answering:
- Start with a direct answer to the question
- Support with evidence from the context
- Mention chapter/section references naturally
- Keep responses focused and relevant"""

        logger.info(f"RAG Agent initialized with model: {self.model}")

    def generate_answer(
        self,
        query: str,
        session_id: Optional[str] = None,
        chapter_filter: Optional[int] = None,
    ) -> Dict:
        """
        Generate grounded answer for user query.

        Pipeline:
        1. Retrieve relevant chunks from vector store
        2. Rerank chunks for relevance
        3. Assemble context from top chunks
        4. Generate answer with LLM
        5. Extract citations

        Args:
            query: User question
            session_id: Optional session ID for context
            chapter_filter: Optional chapter number to filter results

        Returns:
            Dict with:
                - answer: str (generated answer)
                - citations: List[Dict] (chapter/section references)
                - retrieval_score: float (top similarity score)
                - chunks_used: int (number of context chunks)
                - fallback: bool (whether fallback response was used)
        """
        logger.info(f"Generating answer for query: {query[:50]}...")

        # Step 1: Retrieve relevant chunks
        try:
            retrieved_chunks = self.retriever.retrieve(
                query=query, top_k=10, chapter_filter=chapter_filter
            )

            if not retrieved_chunks:
                logger.warning("No chunks retrieved from vector store")
                return self._fallback_response()

            # Step 2: Rerank chunks
            reranked_chunks = self.reranker.rerank(
                query=query, chunks=retrieved_chunks, top_n=5
            )

            if not reranked_chunks:
                logger.warning("No chunks after reranking")
                return self._fallback_response()

            # Check top retrieval score for confidence threshold
            top_score = reranked_chunks[0].get("score", 0.0)
            if top_score < settings.RETRIEVAL_CONFIDENCE_THRESHOLD:
                logger.info(
                    f"Top score {top_score} below threshold {settings.RETRIEVAL_CONFIDENCE_THRESHOLD}"
                )
                return self._fallback_response()

            # Step 3: Assemble context
            context = self._assemble_context(reranked_chunks)

            # Step 4: Generate answer
            answer = self._call_llm(query=query, context=context)

            # Step 5: Extract citations
            citations = self._extract_citations(reranked_chunks)

            return {
                "answer": answer,
                "citations": citations,
                "retrieval_score": top_score,
                "chunks_used": len(reranked_chunks),
                "fallback": False,
            }

        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}", exc_info=True)
            raise

    def _assemble_context(self, chunks: List[Dict]) -> str:
        """
        Assemble context string from retrieved chunks.

        Args:
            chunks: List of chunk dictionaries with content and metadata

        Returns:
            Formatted context string for LLM
        """
        context_parts = []

        for i, chunk in enumerate(chunks, 1):
            chapter_title = chunk.get("chapter_title", "Unknown Chapter")
            section_name = chunk.get("section_name", "")
            content = chunk.get("content", "")

            # Format: [Chapter Title - Section] Content
            header = f"[{chapter_title}"
            if section_name:
                header += f" - {section_name}"
            header += "]"

            context_parts.append(f"{header}\n{content}\n")

        context = "\n".join(context_parts)

        logger.debug(f"Assembled context from {len(chunks)} chunks ({len(context)} chars)")

        return context

    def _call_llm(self, query: str, context: str) -> str:
        """
        Call OpenAI Chat Completions API to generate answer.

        Args:
            query: User question
            context: Retrieved context

        Returns:
            Generated answer
        """
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"""Context from the book:

{context}

---

Question: {query}

Answer the question based ONLY on the context above. Include chapter/section references in your answer.""",
                },
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Low temperature for factual accuracy
                max_tokens=500,  # Reasonable answer length
            )

            answer = response.choices[0].message.content.strip()

            logger.info(f"Generated answer ({len(answer)} chars)")

            return answer

        except Exception as e:
            logger.error(f"LLM call failed: {e}", exc_info=True)
            raise

    def _extract_citations(self, chunks: List[Dict]) -> List[Dict]:
        """
        Extract citation information from chunks.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            List of citation dictionaries
        """
        citations = []
        seen_citations = set()  # Deduplicate

        for chunk in chunks:
            chapter_title = chunk.get("chapter_title", "Unknown Chapter")
            section_name = chunk.get("section_name")
            paragraph_index = chunk.get("paragraph_index")

            # Create citation key for deduplication
            citation_key = (chapter_title, section_name)

            if citation_key not in seen_citations:
                citation = {"chapter": chapter_title}

                if section_name:
                    citation["section"] = section_name

                if paragraph_index is not None:
                    citation["paragraph"] = paragraph_index

                citations.append(citation)
                seen_citations.add(citation_key)

        logger.debug(f"Extracted {len(citations)} unique citations")

        return citations

    def _fallback_response(self) -> Dict:
        """
        Return fallback response when no relevant information found.

        Returns:
            Dict with fallback answer and empty citations
        """
        return {
            "answer": "I cannot answer this from the book content. This information is not covered in 'Physical AI & Humanoid Robotics Essentials'.",
            "citations": [],
            "retrieval_score": 0.0,
            "chunks_used": 0,
            "fallback": True,
        }

    def generate_answer_with_fallback(
        self,
        query: str,
        session_id: Optional[str] = None,
        chapter_filter: Optional[int] = None,
    ) -> Dict:
        """
        Generate answer with automatic fallback to OpenAI for out-of-scope queries.

        Decision Flow:
        1. Classify query (in-scope vs out-of-scope)
        2. If IN_SCOPE → RAG pipeline (retrieve + cite)
        3. If OUT_OF_SCOPE → Direct OpenAI (no retrieval)
        4. If RAG fails (low confidence) → OpenAI fallback

        Returns:
            Dict with:
                - answer: str
                - citations: List[Dict] (empty for fallback)
                - retrieval_score: float
                - chunks_used: int
                - fallback: bool
                - answer_type: "BOOK" or "GENERAL_AI"
        """
        from agents.query_classifier import get_classifier

        logger.info(f"Processing query with fallback: {query[:50]}...")

        # Step 1: Classify query
        classifier = get_classifier()
        classification = classifier.classify(query)

        # Step 2: Route based on classification
        if classification == "OUT_OF_SCOPE":
            logger.info("Query is OUT_OF_SCOPE - using OpenAI fallback")
            return self._openai_fallback(query)

        # Step 3: Try RAG pipeline for IN_SCOPE queries
        try:
            result = self.generate_answer(
                query=query,
                session_id=session_id,
                chapter_filter=chapter_filter
            )

            # Check if RAG found good results
            if result["fallback"] or result["retrieval_score"] < 0.5:
                logger.warning("RAG confidence too low - using OpenAI fallback")
                return self._openai_fallback(query)

            # Success - return RAG result
            result["answer_type"] = "BOOK"
            return result

        except Exception as e:
            logger.error(f"RAG pipeline failed: {e} - using OpenAI fallback")
            return self._openai_fallback(query)

    def _openai_fallback(self, query: str) -> Dict:
        """
        Direct OpenAI answer for general questions (no RAG).

        Returns answer clearly labeled as "General AI Answer".
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful AI assistant specializing in Physical AI and Robotics.

The user asked a question that is outside the scope of the specific book "Physical AI & Humanoid Robotics Essentials".

Provide a helpful, accurate answer based on your general knowledge. Keep responses concise and informative.

IMPORTANT: Your answer will be labeled as "General AI Answer" to distinguish it from book-based responses."""
                },
                {
                    "role": "user",
                    "content": query
                }
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )

            answer = response.choices[0].message.content.strip()

            logger.info(f"Generated OpenAI fallback answer ({len(answer)} chars)")

            return {
                "answer": answer,
                "citations": [],
                "retrieval_score": 0.0,
                "chunks_used": 0,
                "fallback": True,
                "answer_type": "GENERAL_AI"
            }

        except Exception as e:
            logger.error(f"OpenAI fallback failed: {e}")
            return {
                "answer": "I apologize, but I'm unable to answer that question right now. Please try again later.",
                "citations": [],
                "retrieval_score": 0.0,
                "chunks_used": 0,
                "fallback": True,
                "answer_type": "ERROR"
            }


# Global agent instance (singleton pattern)
_agent_instance = None


def get_rag_agent() -> RAGAgent:
    """
    Get global RAG agent instance (singleton).

    Returns:
        RAGAgent: Configured agent instance
    """
    global _agent_instance

    if _agent_instance is None:
        _agent_instance = RAGAgent()

    return _agent_instance
