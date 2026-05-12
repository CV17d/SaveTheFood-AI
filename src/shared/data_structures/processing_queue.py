"""
ProcessingQueue — Queue (FIFO) Data Structure.

PURPOSE:
    Manages the asynchronous processing pipeline for uploaded receipt images.
    Images are enqueued as they are uploaded and dequeued in order for OCR
    processing, ensuring fair First-In, First-Out scheduling.

WHERE USED:
    - src/application/use_cases/process_receipt_usecase.py → Pipeline orchestration.
    - src/presentation/app.py → Upload handler enqueues images.

COMPLEXITY:
    - enqueue(): O(1)
    - dequeue(): O(1) (using collections.deque)
    - peek():    O(1)

WHY:
    A queue ensures receipts are processed in upload order, preventing
    starvation of earlier uploads when multiple images are submitted rapidly.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class QueuedReceipt:
    """Represents a receipt waiting in the processing queue."""

    receipt_id: str
    image_path: str
    priority: int = 0  # 0 = normal, 1 = high (manual re-processing)


class ProcessingQueue(Generic[T]):
    """
    Generic FIFO Queue for receipt processing pipeline.

    Uses collections.deque for O(1) enqueue/dequeue operations,
    unlike a list which has O(n) for popleft.

    Attributes:
        _queue: Internal deque storage.
        _max_size: Maximum queue capacity (backpressure).
    """

    def __init__(self, max_size: int = 1000) -> None:
        self._queue: deque[T] = deque(maxlen=max_size)
        self._max_size = max_size

    def enqueue(self, item: T) -> bool:
        """
        Add an item to the back of the queue. O(1).

        Returns:
            True if enqueued successfully, False if queue is full.
        """
        if len(self._queue) >= self._max_size:
            return False
        self._queue.append(item)
        return True

    def dequeue(self) -> T:
        """
        Remove and return the front item. O(1).

        Raises:
            IndexError: If the queue is empty.
        """
        if self.is_empty:
            raise IndexError("Cannot dequeue from an empty ProcessingQueue.")
        return self._queue.popleft()

    def peek(self) -> T:
        """
        View the front item without removing it. O(1).

        Raises:
            IndexError: If the queue is empty.
        """
        if self.is_empty:
            raise IndexError("Cannot peek an empty ProcessingQueue.")
        return self._queue[0]

    @property
    def is_empty(self) -> bool:
        return len(self._queue) == 0

    @property
    def size(self) -> int:
        return len(self._queue)

    @property
    def is_full(self) -> bool:
        return len(self._queue) >= self._max_size

    def clear(self) -> None:
        self._queue.clear()

    def __repr__(self) -> str:
        return f"ProcessingQueue(size={self.size}, max_size={self._max_size})"
