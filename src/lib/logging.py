"""Logging utilities."""

import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = None, format_string: Optional[str] = None) -> None:
    """Setup global logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
    """
    # Set default format if not provided
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Set default level if not provided
    if level is None:
        level = 'WARNING'

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        stream=sys.stdout
    )


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Logger name (usually __name__)
        level: Optional log level override

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Don't add handlers if they already exist - let the root logger handle everything
    if not logger.handlers:
        # Set log level to NOTSET so it inherits from root logger
        logger.setLevel(logging.NOTSET)

    return logger