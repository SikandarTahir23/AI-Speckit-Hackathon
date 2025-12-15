"""
Chunker - Text Chunking with Sentence Boundary Splitting

Splits text into 512-token chunks with 50-token overlap.
Implements research.md Task 2: Chunking Strategy.
"""

from typing import List, Dict, Optional
import re
import tiktoken
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Chunker:
    """
    Text chunker with sentence-boundary splitting.

    Splits text into fixed-size chunks while respecting sentence boundaries
    to maintain semantic coherence. Uses tiktoken for accurate token counting.
    """

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        """
        Initialize chunker with configuration.

        Args:
            chunk_size: Maximum tokens per chunk (default from settings: 512)
            chunk_overlap: Overlap tokens between chunks (default from settings: 50)
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        # Initialize tiktoken encoder for GPT-3.5/4 token counting
        self.encoding = tiktoken.get_encoding("cl100k_base")

        logger.info(
            f"Chunker initialized: {self.chunk_size} tokens/chunk, {self.chunk_overlap} overlap"
        )

    def chunk_text(self, text: str) -> List[Dict[str, any]]:
        """
        Split text into chunks with sentence-boundary awareness.

        Args:
            text: Input text to chunk

        Returns:
            List of chunk dictionaries with 'content', 'token_count', 'char_count', 'index'

        Example:
            [
                {
                    "content": "First chunk text...",
                    "token_count": 487,
                    "char_count": 1950,
                    "index": 0
                },
                ...
            ]
        """
        if not text or not text.strip():
            return []

        # Split text into sentences
        sentences = self._split_sentences(text)

        # Build chunks from sentences
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_tokens = len(self.encoding.encode(sentence))

            # If single sentence exceeds chunk_size, split it forcefully
            if sentence_tokens > self.chunk_size:
                # Flush current chunk if not empty
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, chunk_index))
                    chunk_index += 1
                    current_chunk = []
                    current_tokens = 0

                # Split long sentence into smaller pieces
                sub_chunks = self._split_long_sentence(sentence)
                for sub_chunk in sub_chunks:
                    chunks.append(self._create_chunk([sub_chunk], chunk_index))
                    chunk_index += 1

                continue

            # Check if adding sentence exceeds chunk_size
            if current_tokens + sentence_tokens > self.chunk_size:
                # Save current chunk
                chunks.append(self._create_chunk(current_chunk, chunk_index))
                chunk_index += 1

                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(
                    current_chunk, self.chunk_overlap
                )
                current_chunk = overlap_sentences + [sentence]
                current_tokens = sum(
                    len(self.encoding.encode(s)) for s in current_chunk
                )
            else:
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_tokens += sentence_tokens

        # Add final chunk if not empty
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, chunk_index))

        logger.info(f"Chunked text into {len(chunks)} chunks")

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using regex.

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Split on sentence boundaries: ., !, ? followed by whitespace
        # Keep the punctuation with the sentence
        pattern = r'(?<=[.!?])\s+'
        sentences = re.split(pattern, text)

        # Remove empty strings and strip whitespace
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _split_long_sentence(self, sentence: str) -> List[str]:
        """
        Force-split a sentence that exceeds chunk_size.

        Args:
            sentence: Long sentence to split

        Returns:
            List of sentence fragments
        """
        tokens = self.encoding.encode(sentence)
        fragments = []

        for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
            fragment_tokens = tokens[i : i + self.chunk_size]
            fragment_text = self.encoding.decode(fragment_tokens)
            fragments.append(fragment_text)

        return fragments

    def _get_overlap_sentences(
        self, sentences: List[str], target_overlap_tokens: int
    ) -> List[str]:
        """
        Get sentences from end of list that fit within overlap budget.

        Args:
            sentences: List of sentences
            target_overlap_tokens: Target overlap in tokens

        Returns:
            List of sentences for overlap
        """
        overlap_sentences = []
        overlap_tokens = 0

        # Work backwards from end of sentence list
        for sentence in reversed(sentences):
            sentence_tokens = len(self.encoding.encode(sentence))

            if overlap_tokens + sentence_tokens <= target_overlap_tokens:
                overlap_sentences.insert(0, sentence)
                overlap_tokens += sentence_tokens
            else:
                break

        return overlap_sentences

    def _create_chunk(self, sentences: List[str], index: int) -> Dict[str, any]:
        """
        Create chunk dictionary from list of sentences.

        Args:
            sentences: List of sentences
            index: Chunk index

        Returns:
            Chunk dictionary with content, token_count, char_count, index
        """
        content = " ".join(sentences)
        token_count = len(self.encoding.encode(content))
        char_count = len(content)

        return {
            "content": content,
            "token_count": token_count,
            "char_count": char_count,
            "index": index,
        }

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Input text

        Returns:
            int: Number of tokens
        """
        return len(self.encoding.encode(text))


# Global chunker instance (singleton pattern)
_chunker_instance = None


def get_chunker() -> Chunker:
    """
    Get global chunker instance (singleton).

    Returns:
        Chunker: Configured chunker instance
    """
    global _chunker_instance

    if _chunker_instance is None:
        _chunker_instance = Chunker()

    return _chunker_instance


def process_book(book_content: str) -> List[Dict[str, any]]:
    """
    Process book content from markdown format into structured chunks.

    Parses markdown file, extracts chapters and sections, and chunks content
    with metadata preservation.

    Args:
        book_content: Full book text in markdown format

    Returns:
        List of chapter dictionaries with chunks:
        [
            {
                "chapter_number": 1,
                "chapter_title": "Introduction to Physical AI",
                "chunks": [
                    {
                        "content": "...",
                        "token_count": 487,
                        "char_count": 1950,
                        "index": 0,
                        "section_name": "1.1 Overview",
                        "paragraph_index": 0
                    },
                    ...
                ]
            },
            ...
        ]
    """
    chunker = get_chunker()
    chapters = []

    # Split content by chapter headers (markdown # Chapter N: Title)
    chapter_pattern = r'^#\s+Chapter\s+(\d+):\s+(.+)$'
    section_pattern = r'^##\s+(\d+\.\d+)\s+(.+)$'

    lines = book_content.split('\n')
    current_chapter = None
    current_section = None
    current_content = []

    for line in lines:
        chapter_match = re.match(chapter_pattern, line, re.IGNORECASE)
        section_match = re.match(section_pattern, line)

        if chapter_match:
            # Save previous chapter's content
            if current_chapter and current_content:
                _process_chapter_content(
                    current_chapter, current_content, current_section, chunker
                )
                chapters.append(current_chapter)

            # Start new chapter
            chapter_num = int(chapter_match.group(1))
            chapter_title = chapter_match.group(2).strip()
            current_chapter = {
                "chapter_number": chapter_num,
                "chapter_title": f"Chapter {chapter_num}: {chapter_title}",
                "chunks": []
            }
            current_content = []
            current_section = None

        elif section_match and current_chapter:
            # Save previous section's content
            if current_content:
                _process_chapter_content(
                    current_chapter, current_content, current_section, chunker
                )
                current_content = []

            # Start new section
            section_num = section_match.group(1)
            section_title = section_match.group(2).strip()
            current_section = f"{section_num} {section_title}"

        elif current_chapter:
            # Accumulate content for current section/chapter
            current_content.append(line)

    # Save final chapter
    if current_chapter and current_content:
        _process_chapter_content(
            current_chapter, current_content, current_section, chunker
        )
        chapters.append(current_chapter)

    total_chunks = sum(len(ch["chunks"]) for ch in chapters)
    logger.info(
        f"Processed book into {len(chapters)} chapters with {total_chunks} total chunks"
    )

    return chapters


def _process_chapter_content(
    chapter: Dict,
    content_lines: List[str],
    section_name: Optional[str],
    chunker: Chunker
):
    """
    Process content lines into chunks and add to chapter.

    Args:
        chapter: Chapter dictionary to add chunks to
        content_lines: Lines of content to chunk
        section_name: Current section name (or None)
        chunker: Chunker instance
    """
    # Join lines and clean up
    content = '\n'.join(content_lines).strip()

    if not content:
        return

    # Chunk the content
    chunks = chunker.chunk_text(content)

    # Add metadata to each chunk
    for chunk in chunks:
        chunk["section_name"] = section_name or ""
        chunk["chapter_number"] = chapter["chapter_number"]
        chunk["chapter_title"] = chapter["chapter_title"]
        chunk["paragraph_index"] = len(chapter["chunks"])  # Sequential index within chapter

    chapter["chunks"].extend(chunks)
