"""
ExpirationHeap — Heap / Priority Queue Data Structure.

PURPOSE:
    Automatically sorts the food inventory by expiration_date so that
    the most urgent items to consume are always extractable in O(log N).
    This powers the "Expiring Soon" dashboard widget and the ingredient
    prioritization for recipe generation.

WHERE USED:
    - src/application/use_cases/generate_recipe_usecase.py → Extract top-N
      most urgent ingredients for recipe generation.
    - src/presentation/pages/inventory.py → "Expiring Soon" sorted display.
    - src/application/services/dashboard_metrics_service.py → Urgency stats.

COMPLEXITY:
    - insert():       O(log N)
    - extract_min():  O(log N)   — item expiring soonest
    - peek_min():     O(1)
    - build heap:     O(N)

WHY:
    A min-heap is optimal for repeatedly extracting the minimum element
    (earliest expiration) without sorting the entire collection each time.
    Sorting would cost O(N log N) per query; a heap gives O(log N).
"""

from __future__ import annotations

import heapq
from typing import Generic, TypeVar

T = TypeVar("T")


class ExpirationHeap(Generic[T]):
    """
    Min-Heap Priority Queue for expiring food items.

    Items must implement __lt__ for comparison (FoodItem does this
    by comparing expiration_date).

    Internally uses Python's heapq module which provides a min-heap.
    """

    def __init__(self) -> None:
        self._heap: list[T] = []

    def insert(self, item: T) -> None:
        """
        Insert an item into the heap. O(log N).

        Maintains the heap invariant after insertion.
        """
        heapq.heappush(self._heap, item)

    def extract_min(self) -> T:
        """
        Remove and return the item with the earliest expiration. O(log N).

        Raises:
            IndexError: If the heap is empty.
        """
        if self.is_empty:
            raise IndexError("Cannot extract from an empty ExpirationHeap.")
        return heapq.heappop(self._heap)

    def peek_min(self) -> T:
        """
        View the most urgent item without removing it. O(1).

        Raises:
            IndexError: If the heap is empty.
        """
        if self.is_empty:
            raise IndexError("Cannot peek an empty ExpirationHeap.")
        return self._heap[0]

    def extract_top_n(self, n: int) -> list[T]:
        """
        Extract the N most urgent items. O(N log N).

        Returns up to N items; if heap has fewer, returns all.
        """
        result: list[T] = []
        for _ in range(min(n, self.size)):
            result.append(self.extract_min())
        return result

    def build_from(self, items: list[T]) -> None:
        """
        Build the heap from a list of items. O(N).

        More efficient than inserting one by one (O(N) vs O(N log N)).
        """
        self._heap = list(items)
        heapq.heapify(self._heap)

    @property
    def is_empty(self) -> bool:
        return len(self._heap) == 0

    @property
    def size(self) -> int:
        return len(self._heap)

    def clear(self) -> None:
        self._heap.clear()

    def __repr__(self) -> str:
        return f"ExpirationHeap(size={self.size})"
