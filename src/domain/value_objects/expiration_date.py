"""
ExpirationDate Value Object.

Immutable value object encapsulating expiration date computation logic.
Uses the shelf-life Dictionary/Hashmap for O(1) lookups.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class ExpirationDate:
    """
    Immutable Value Object representing an estimated expiration date.

    Attributes:
        estimated_date: The computed expiration date.
        confidence: Confidence level of the estimate ("high" | "medium" | "low").
        source: How the date was determined ("shelf_life_map" | "llm_estimate" | "user_input").
    """

    estimated_date: date
    confidence: str = "medium"
    source: str = "shelf_life_map"

    @staticmethod
    def from_shelf_life(
        purchase_date: date,
        shelf_life_days: int,
        source: str = "shelf_life_map",
    ) -> ExpirationDate:
        """
        Factory method: compute expiration from purchase date + shelf-life days.

        Uses the Dictionary/Hashmap shelf-life lookup result.
        """
        return ExpirationDate(
            estimated_date=purchase_date + timedelta(days=shelf_life_days),
            confidence="high" if source == "shelf_life_map" else "medium",
            source=source,
        )

    @property
    def days_remaining(self) -> int:
        """Days until expiration from today."""
        return (self.estimated_date - date.today()).days

    @property
    def is_expired(self) -> bool:
        return self.days_remaining < 0
