"""
Shared Utilities — helper functions used across layers.
"""

from __future__ import annotations

import re


def normalize_food_name(raw_name: str) -> str:
    """
    Normalize a raw OCR-extracted food name.

    Strips whitespace, removes non-alphanumeric chars (except spaces),
    and converts to title case.
    """
    cleaned = re.sub(r"[^a-zA-ZáéíóúñÁÉÍÓÚÑ\s]", "", raw_name)
    return cleaned.strip().title()


def truncate(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis if it exceeds max_length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
