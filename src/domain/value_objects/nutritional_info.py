"""
NutritionalInfo Value Object.

Immutable value object for nutritional data associated with food items.
Used in the Food Category Tree for aggregated nutritional reporting.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NutritionalInfo:
    """
    Immutable Value Object for nutritional metadata.

    All values are per 100g serving.
    """

    calories_kcal: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    fiber_g: float = 0.0

    @property
    def is_empty(self) -> bool:
        """Check if all nutritional values are zero (no data)."""
        return all(
            v == 0.0
            for v in (
                self.calories_kcal,
                self.protein_g,
                self.carbs_g,
                self.fat_g,
                self.fiber_g,
            )
        )
