"""
Recipe DTOs — data transfer objects for recipe display.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RecipeDTO:
    """Read-only DTO for displaying a recipe in the UI."""

    id: str
    title: str
    description: str
    ingredients: list[str]
    steps: list[str]
    estimated_time_minutes: int
    servings: int
    tags: list[str]
    relevance_score: float
    matched_expiring_count: int
