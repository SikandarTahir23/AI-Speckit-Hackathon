"""
Structured Logging Setup

Provides JSON-formatted logging with correlation IDs for request tracing.
Follows constitutional requirement VI: Observability & Production Readiness.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
import uuid


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with JSON formatting

    Args:
        name: Logger name (typically __name__ from calling module)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Console handler with JSON formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def generate_request_id() -> str:
    """Generate a unique request ID for correlation"""
    return f"req_{uuid.uuid4().hex[:12]}"


class RequestLogger:
    """Context manager for request-scoped logging with correlation ID"""

    def __init__(self, logger: logging.Logger, request_id: str = None):
        """
        Initialize request logger

        Args:
            logger: Logger instance
            request_id: Optional request ID (generated if not provided)
        """
        self.logger = logger
        self.request_id = request_id or generate_request_id()
        self.start_time = None

    def __enter__(self):
        """Enter context - record start time"""
        self.start_time = datetime.utcnow()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - log duration and any errors"""
        if self.start_time:
            duration_ms = (datetime.utcnow() - self.start_time).total_seconds() * 1000
            self.info(f"Request completed in {duration_ms:.2f}ms", duration_ms=duration_ms)

        if exc_type is not None:
            self.error(f"Request failed: {exc_val}", exception_type=exc_type.__name__)

    def _log(self, level: str, message: str, **kwargs):
        """Internal logging method with correlation ID"""
        extra_data = {
            "request_id": self.request_id,
            **kwargs,
        }
        log_func = getattr(self.logger, level)
        log_func(message, extra={"request_id": self.request_id, "extra_data": extra_data})

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log("debug", message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log("info", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log("warning", message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log("error", message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log("critical", message, **kwargs)


# Example usage:
# from utils.logger import setup_logger, RequestLogger
#
# logger = setup_logger(__name__)
#
# with RequestLogger(logger) as req_logger:
#     req_logger.info("Processing chat request", endpoint="/chat", user_id="123")
#     # ... do work ...
#     req_logger.info("Retrieved chunks from Qdrant", chunk_count=5)
