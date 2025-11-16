"""Logging configuration for the application."""

from __future__ import annotations

import logging
import sys
from typing import Optional

from .constants import LOG_DATE_FORMAT, LOG_FORMAT


def configure_logging(level: Optional[str] = None) -> None:
    """Configure application-wide logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               Defaults to INFO.
    """
    if level is None:
        level = "INFO"

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        stream=sys.stdout,
    )

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("rpy2").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


__all__ = ["configure_logging", "get_logger"]
