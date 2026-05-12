"""
FoodItem Entity.

Represents a single food product extracted from a receipt.
Each item carries an estimated expiration date (Value Object)
and belongs to a category within the Food Category Tree.

Data Structures Used:
    - Dictionary/Hashmap: Shelf-life lookup in O(1) to estimate expiration.
    - Heap (Priority Queue): FoodItems are inserted into a min-heap
      ordered by expiration_date for O(log N) extraction of the most
      urgent items to consume.
    - Trie/N-ary Tree: Category path (e.g., Dairy → Cheese → Cheddar)
      stored as a list of strings for hierarchical grouping.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class FoodItem:
    """
    Domain Entity: a food product with expiration tracking.

    Attributes:
        id: Unique identifier (UUID).
        name: Product name as extracted/normalized from OCR.
        quantity: Number of units purchased.
        unit: Unit of measurement (e.g., "kg", "units", "L").
        purchase_date: Date the item was purchased (from receipt).
        expiration_date: Estimated expiration date (computed via shelf-life map).
        category_path: Hierarchical category path for the Food Category Tree,
                       e.g., ["Dairy", "Cheese", "Cheddar"].
        confidence_score: OCR extraction confidence (0.0 – 1.0).
        receipt_id: Foreign key linking back to the parent Receipt.
    """

    name: str
    quantity: float = 1.0
    unit: str = "units"
    purchase_date: date = field(default_factory=date.today)
    expiration_date: date | None = None
    category_path: list[str] = field(default_factory=list)
    confidence_score: float = 1.0
    receipt_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)

    # ─── Domain Logic ─────────────────────────────────────

    @property
    def days_until_expiration(self) -> int | None:
        """
        Compute days remaining until expiration.

        Returns:
            Positive int if still fresh, negative if expired, None if unknown.
        """
        if self.expiration_date is None:
            return None
        return (self.expiration_date - date.today()).days

    @property
    def is_expired(self) -> bool:
        """Check if the item has passed its expiration date."""
        days = self.days_until_expiration
        return days is not None and days < 0

    @property
    def urgency_level(self) -> str:
        """
        Classify urgency for UI display.

        Returns:
            "EXPIRED" | "CRITICAL" (≤2 days) | "WARNING" (≤5 days) | "OK"
        """
        days = self.days_until_expiration
        if days is None:
            return "UNKNOWN"
        if days < 0:
            return "EXPIRED"
        if days <= 2:
            return "CRITICAL"
        if days <= 5:
            return "WARNING"
        return "OK"

    def __lt__(self, other: FoodItem) -> bool:
        """
        Comparison operator for heap ordering.

        Items with earlier expiration dates have higher priority.
        Items with no expiration date sort to the end.
        """
        if self.expiration_date is None:
            return False
        if other.expiration_date is None:
            return True
        return self.expiration_date < other.expiration_date

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FoodItem):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
