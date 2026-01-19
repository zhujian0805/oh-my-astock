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
        level = 'INFO'

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

    # Only configure if not already configured
    if not logger.handlers:
        # Set log level
        log_level = getattr(logging, level.upper()) if level else logging.INFO
        logger.setLevel(log_level)

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger