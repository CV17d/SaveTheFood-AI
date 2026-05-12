"""
UndoStack — Stack (LIFO) Data Structure.

PURPOSE:
    Implements a "Rollback/Undo" feature in the Streamlit UI for when
    users manually correct OCR extraction errors. Each correction is
    pushed onto the stack, and users can undo corrections in reverse
    chronological order (Last-In, First-Out).

WHERE USED:
    - src/presentation/pages/inventory.py → Manual OCR correction UI.
    - The stack stores (field_name, old_value, new_value) tuples.

COMPLEXITY:
    - push(): O(1)
    - pop():  O(1)
    - peek(): O(1)

WHY:
    A stack is the natural data structure for undo operations because
    the most recent change is always the first to be reversed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class UndoAction:
    """Represents a single undoable action."""

    field_name: str
    old_value: str
    new_value: str
    item_id: str
    description: str = ""


class UndoStack(Generic[T]):
    """
    Generic LIFO Stack for undo operations.

    Attributes:
        _items: Internal list used as stack storage.
        _max_size: Maximum stack depth (prevents unbounded memory growth).
    """

    def __init__(self, max_size: int = 100) -> None:
        self._items: list[T] = []
        self._max_size = max_size

    def push(self, item: T) -> None:
        """
        Push an item onto the stack. O(1).

        If the stack is at max capacity, the oldest item is discarded.
        """
        if len(self._items) >= self._max_size:
            self._items.pop(0)  # Discard oldest (bottom of stack)
        self._items.append(item)

    def pop(self) -> T:
        """
        Pop the most recent item from the stack. O(1).

        Raises:
            IndexError: If the stack is empty.
        """
        if self.is_empty:
            raise IndexError("Cannot pop from an empty UndoStack.")
        return self._items.pop()

    def peek(self) -> T:
        """
        View the top item without removing it. O(1).

        Raises:
            IndexError: If the stack is empty.
        """
        if self.is_empty:
            raise IndexError("Cannot peek an empty UndoStack.")
        return self._items[-1]

    @property
    def is_empty(self) -> bool:
        """Check if the stack has no items."""
        return len(self._items) == 0

    @property
    def size(self) -> int:
        """Current number of items in the stack."""
        return len(self._items)

    def clear(self) -> None:
        """Remove all items from the stack."""
        self._items.clear()

    def __repr__(self) -> str:
        return f"UndoStack(size={self.size}, max_size={self._max_size})"
