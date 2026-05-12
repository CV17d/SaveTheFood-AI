"""
Structured Logging Configuration.

Provides a pre-configured logger with JSON-compatible output
for observability across all layers.
"""

from __future__ import annotations

import logging
import sys


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Create a structured logger with console output.

    Args:
        name: Logger name (typically __name__).
        level: Logging level string.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
