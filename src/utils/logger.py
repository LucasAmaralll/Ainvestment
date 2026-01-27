"""
Structured logging using structlog.
Provides JSON-formatted logs for observability.
"""

import sys
import logging
import structlog
from typing import Any

from src.utils.config import settings


def setup_logging():
    """Configure structured logging."""
    
    # Map log level string to logging constant
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = log_level_map.get(settings.log_level.upper(), logging.INFO)
    
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


# Initialize logging on module import
setup_logging()

# Export logger
logger = structlog.get_logger()


def log_event(event: str, **kwargs: Any) -> None:
    """
    Log a structured event with additional context.
    
    Usage:
        log_event("stock_fetched", ticker="AAPL", rows=252, duration_ms=1234)
    """
    logger.info(event, **kwargs)


def log_error(error: Exception, context: dict[str, Any] | None = None) -> None:
    """
    Log an error with context.
    
    Usage:
        try:
            ...
        except Exception as e:
            log_error(e, {"ticker": "AAPL", "operation": "fetch"})
    """
    logger.error(
        "error_occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        **(context or {})
    )
