"""
Receipt DTOs — data transfer objects for the presentation layer.

These are flat, serializable structures that decouple the domain
entities from the UI layer. The presentation layer NEVER receives
raw domain entities.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReceiptDTO:
    """Read-only DTO for displaying a receipt in the UI."""

    id: str
    image_path: str
    state: str
    item_count: int
    uploaded_at: str
    failure_reason: str | None = None


@dataclass(frozen=True)
class FoodItemDTO:
    """Read-only DTO for displaying a food item in the UI."""

    id: str
    name: str
    quantity: float
    unit: str
    purchase_date: str
    expiration_date: str | None
    days_remaining: int | None
    urgency_level: str
    category: str
