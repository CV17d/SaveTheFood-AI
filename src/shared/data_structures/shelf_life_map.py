"""
ShelfLifeMap — Dictionary/Hashmap Data Structure.

PURPOSE: O(1) lookups of standard food shelf-life rules.
WHERE: src/application/use_cases/process_receipt_usecase.py → expiration estimation.
WHY: Hashmaps provide constant-time lookup, critical for real-time processing.
"""

from __future__ import annotations


class ShelfLifeMap:
    """
    Hashmap for O(1) food shelf-life lookups (days).

    Pre-populated with common food items. Falls back to LLM estimation
    for unknown items via ShelfLifeNotFoundError.
    """

    # Default shelf-life database (days from purchase)
    _DEFAULT_DATA: dict[str, int] = {
        # Dairy
        "milk": 7, "yogurt": 14, "cheese": 21, "butter": 30,
        "cream": 7, "sour cream": 14, "cottage cheese": 10,
        # Proteins
        "beef": 3, "chicken": 2, "pork": 3, "fish": 2,
        "ground beef": 2, "turkey": 2, "shrimp": 2, "salmon": 2,
        "eggs": 21, "tofu": 7,
        # Produce — Fruits
        "banana": 5, "apple": 21, "orange": 14, "strawberry": 5,
        "grape": 7, "mango": 5, "avocado": 4, "lemon": 21,
        "blueberry": 7, "peach": 4,
        # Produce — Vegetables
        "lettuce": 7, "tomato": 7, "cucumber": 7, "carrot": 21,
        "broccoli": 5, "spinach": 5, "onion": 30, "potato": 21,
        "bell pepper": 7, "mushroom": 5, "celery": 14, "garlic": 60,
        # Bread & Bakery
        "bread": 5, "tortilla": 7, "bagel": 5, "croissant": 3,
        # Deli
        "ham": 5, "salami": 14, "deli turkey": 5,
        # Beverages
        "juice": 7, "almond milk": 7,
        # Condiments (opened)
        "ketchup": 30, "mustard": 60, "mayonnaise": 14, "salsa": 7,
    }

    def __init__(self, custom_data: dict[str, int] | None = None) -> None:
        self._data: dict[str, int] = dict(self._DEFAULT_DATA)
        if custom_data:
            self._data.update(custom_data)

    def get(self, item_name: str) -> int | None:
        """O(1) shelf-life lookup. Returns days or None."""
        return self._data.get(item_name.lower().strip())

    def set(self, item_name: str, days: int) -> None:
        """Add/update a shelf-life entry. O(1)."""
        self._data[item_name.lower().strip()] = days

    def contains(self, item_name: str) -> bool:
        """Check if item exists in the map. O(1)."""
        return item_name.lower().strip() in self._data

    @property
    def size(self) -> int:
        return len(self._data)

    def all_items(self) -> dict[str, int]:
        """Return a copy of the entire map."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"ShelfLifeMap(entries={self.size})"
