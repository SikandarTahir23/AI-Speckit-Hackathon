"""
Input Validation Functions

Validates user queries and API inputs according to research.md requirements.
"""

from typing import Optional, Tuple
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Validate user query input.

    Checks:
    - Non-empty (not whitespace-only)
    - Within max length (2000 characters per research.md)

    Args:
        query: User question text

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if query passes all checks
        - error_message: None if valid, otherwise error description
    """
    # Check for None
    if query is None:
        return False, "Query cannot be None"

    # Strip whitespace
    query_stripped = query.strip()

    # Check for empty query
    if not query_stripped:
        return False, "Query cannot be empty or whitespace-only"

    # Check length
    if len(query) > settings.MAX_QUERY_LENGTH:
        return (
            False,
            f"Query too long ({len(query)} chars). Maximum is {settings.MAX_QUERY_LENGTH} characters.",
        )

    # All checks passed
    return True, None


def validate_session_id(session_id: str) -> Tuple[bool, Optional[str]]:
    """
    Validate session ID format.

    Checks:
    - Non-empty
    - Valid UUID v4 format (36 characters with hyphens)

    Args:
        session_id: Session identifier

    Returns:
        Tuple of (is_valid, error_message)
    """
    import uuid

    if not session_id or not session_id.strip():
        return False, "Session ID cannot be empty"

    try:
        # Try to parse as UUID
        uuid.UUID(session_id, version=4)
        return True, None
    except ValueError:
        return False, f"Invalid session ID format. Must be a valid UUID v4."


def validate_chapter_number(chapter_number: int) -> Tuple[bool, Optional[str]]:
    """
    Validate chapter number.

    Checks:
    - Positive integer
    - Within reasonable range (1-100)

    Args:
        chapter_number: Chapter number

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(chapter_number, int):
        return False, "Chapter number must be an integer"

    if chapter_number < 1:
        return False, "Chapter number must be positive (>= 1)"

    if chapter_number > 100:
        return False, "Chapter number too large (max 100)"

    return True, None


def validate_pagination(limit: int, offset: int) -> Tuple[bool, Optional[str]]:
    """
    Validate pagination parameters.

    Checks:
    - limit: Positive integer, max 100
    - offset: Non-negative integer

    Args:
        limit: Number of results per page
        offset: Number of results to skip

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(limit, int) or not isinstance(offset, int):
        return False, "Limit and offset must be integers"

    if limit < 1:
        return False, "Limit must be positive (>= 1)"

    if limit > 100:
        return False, "Limit too large (max 100)"

    if offset < 0:
        return False, "Offset cannot be negative"

    return True, None


def sanitize_query(query: str) -> str:
    """
    Sanitize user query by removing dangerous characters and normalizing whitespace.

    Args:
        query: Raw user input

    Returns:
        Sanitized query string
    """
    # Strip leading/trailing whitespace
    query = query.strip()

    # Normalize internal whitespace (replace multiple spaces with single space)
    import re

    query = re.sub(r"\s+", " ", query)

    # Remove null bytes
    query = query.replace("\x00", "")

    return query


def validate_and_sanitize_query(query: str) -> str:
    """
    Validate and sanitize query in one step.

    Args:
        query: Raw user query

    Returns:
        Sanitized query string

    Raises:
        ValidationError: If query fails validation
    """
    # Validate first
    is_valid, error = validate_query(query)

    if not is_valid:
        logger.warning(f"Query validation failed: {error}")
        raise ValidationError(error, field="query")

    # Sanitize and return
    sanitized = sanitize_query(query)

    logger.debug(f"Query validated and sanitized (length: {len(sanitized)} chars)")

    return sanitized


def validate_book_path(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate book file path.

    Checks:
    - Non-empty
    - Has .md extension
    - Path exists (if checking filesystem)

    Args:
        file_path: Path to book markdown file

    Returns:
        Tuple of (is_valid, error_message)
    """
    import os

    if not file_path or not file_path.strip():
        return False, "File path cannot be empty"

    if not file_path.endswith(".md"):
        return False, "Book file must be a Markdown file (.md extension)"

    # Check if file exists
    if not os.path.exists(file_path):
        return False, f"File does not exist: {file_path}"

    if not os.path.isfile(file_path):
        return False, f"Path is not a file: {file_path}"

    return True, None


# ====================
# Authentication Validation (Hackathon Bonus Feature 1)
# ====================

import re

# T022: Email validation (RFC 5322)

# Simplified RFC 5322 email regex (covers 99% of cases)
EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format according to RFC 5322.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if valid
        - (False, error_message) if invalid

    Examples:
        >>> validate_email("user@example.com")
        (True, None)
        >>> validate_email("invalid.email")
        (False, "Invalid email format")
    """
    if not email:
        return (False, "Email is required")

    if not EMAIL_REGEX.match(email):
        return (False, "Invalid email format")

    return (True, None)


# T023: Password strength validation

def validate_password_strength(password: str, min_length: int = 8) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength (FR-006 from spec.md).

    Requirements:
    - Minimum length (default 8 characters)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit

    Args:
        password: Password to validate
        min_length: Minimum required length (default: 8)

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if valid
        - (False, error_message) if invalid

    Examples:
        >>> validate_password_strength("Password123")
        (True, None)
        >>> validate_password_strength("weak")
        (False, "Password must be at least 8 characters long")
        >>> validate_password_strength("password123")
        (False, "Password must contain at least one uppercase letter")
    """
    if not password:
        return (False, "Password is required")

    # Check minimum length
    if len(password) < min_length:
        return (False, f"Password must be at least {min_length} characters long")

    # Check for at least one uppercase letter
    if not any(c.isupper() for c in password):
        return (False, "Password must contain at least one uppercase letter")

    # Check for at least one lowercase letter
    if not any(c.islower() for c in password):
        return (False, "Password must contain at least one lowercase letter")

    # Check for at least one digit
    if not any(c.isdigit() for c in password):
        return (False, "Password must contain at least one digit")

    return (True, None)
