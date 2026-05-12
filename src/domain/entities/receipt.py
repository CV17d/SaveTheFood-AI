"""
Receipt Entity — Aggregate Root.

Implements the **State Pattern** to manage the receipt lifecycle:
    Uploaded → Processing → Parsed → Completed
                                   → Failed

Each state transition enforces invariants and prevents illegal operations
(e.g., you cannot extract items from a receipt that is still uploading).

Data Structures Used:
    - List[str]: Raw bounding-box text lines extracted by OCR before parsing.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.entities.food_item import FoodItem


# ─── State Pattern — Receipt Lifecycle States ─────────────

class ReceiptState(Enum):
    """Finite states a receipt can occupy during its lifecycle."""

    UPLOADED = auto()
    PROCESSING = auto()
    PARSED = auto()
    FAILED = auto()
    COMPLETED = auto()


class BaseReceiptState(ABC):
    """
    Abstract base for the State Pattern.

    Each concrete state defines which transitions and operations
    are permitted, enforcing the receipt's lifecycle invariants.
    """

    @abstractmethod
    def process(self, receipt: Receipt) -> None:
        """Transition the receipt into the Processing state."""
        ...

    @abstractmethod
    def mark_parsed(self, receipt: Receipt) -> None:
        """Transition the receipt into the Parsed state."""
        ...

    @abstractmethod
    def mark_failed(self, receipt: Receipt, reason: str) -> None:
        """Transition the receipt into the Failed state."""
        ...

    @abstractmethod
    def complete(self, receipt: Receipt) -> None:
        """Transition the receipt into the Completed state."""
        ...


class UploadedState(BaseReceiptState):
    """Receipt has been uploaded but not yet processed."""

    def process(self, receipt: Receipt) -> None:
        receipt._state = ReceiptState.PROCESSING
        receipt._state_handler = ProcessingState()

    def mark_parsed(self, receipt: Receipt) -> None:
        raise InvalidStateTransitionError("UPLOADED", "PARSED")

    def mark_failed(self, receipt: Receipt, reason: str) -> None:
        receipt._state = ReceiptState.FAILED
        receipt._failure_reason = reason
        receipt._state_handler = FailedState()

    def complete(self, receipt: Receipt) -> None:
        raise InvalidStateTransitionError("UPLOADED", "COMPLETED")


class ProcessingState(BaseReceiptState):
    """Receipt is currently being processed by the OCR pipeline."""

    def process(self, receipt: Receipt) -> None:
        raise InvalidStateTransitionError("PROCESSING", "PROCESSING")

    def mark_parsed(self, receipt: Receipt) -> None:
        receipt._state = ReceiptState.PARSED
        receipt._state_handler = ParsedState()

    def mark_failed(self, receipt: Receipt, reason: str) -> None:
        receipt._state = ReceiptState.FAILED
        receipt._failure_reason = reason
        receipt._state_handler = FailedState()

    def complete(self, receipt: Receipt) -> None:
        raise InvalidStateTransitionError("PROCESSING", "COMPLETED")


class ParsedState(BaseReceiptState):
    """Receipt has been successfully parsed; items extracted."""

    def process(self, receipt: Receipt) -> None:
        raise InvalidStateTransitionError("PARSED", "PROCESSING")

    def mark_parsed(self, receipt: Receipt) -> None:
        raise InvalidStateTransitionError("PARSED", "PARSED")

    def mark_failed(self, receipt: Receipt, reason: str) -> None:
        receipt._state = ReceiptState.FAILED
        receipt._failure_reason = reason
        receipt._state_handler = FailedState()

    def complete(self, receipt: Receipt) -> None:
        receipt._state = ReceiptState.COMPLETED
        receipt._state_handler = CompletedState()


class FailedState(BaseReceiptState):
    """Receipt processing has failed."""

    def process(self, receipt: Receipt) -> None:
        # Allow retry: transition back to Processing
        receipt._state = ReceiptState.PROCESSING
        receipt._failure_reason = None
        receipt._state_handler = ProcessingState()

    def mark_parsed(self, receipt: Receipt) -> None:
        raise InvalidStateTransitionError("FAILED", "PARSED")

    def mark_failed(self, receipt: Receipt, reason: str) -> None:
        receipt._failure_reason = reason  # Update reason

    def complete(self, receipt: Receipt) -> None:
        raise InvalidStateTransitionError("FAILED", "COMPLETED")


class CompletedState(BaseReceiptState):
    """Receipt has been fully processed and stored."""

    def process(self, receipt: Receipt) -> None:
        raise InvalidStateTransitionError("COMPLETED", "PROCESSING")

    def mark_parsed(self, receipt: Receipt) -> None:
        raise InvalidStateTransitionError("COMPLETED", "PARSED")

    def mark_failed(self, receipt: Receipt, reason: str) -> None:
        raise InvalidStateTransitionError("COMPLETED", "FAILED")

    def complete(self, receipt: Receipt) -> None:
        raise InvalidStateTransitionError("COMPLETED", "COMPLETED")


class InvalidStateTransitionError(Exception):
    """Raised when an illegal state transition is attempted."""

    def __init__(self, from_state: str, to_state: str) -> None:
        super().__init__(
            f"Invalid state transition: {from_state} → {to_state}"
        )


# ─── Receipt Entity ──────────────────────────────────────

@dataclass
class Receipt:
    """
    Aggregate Root representing a supermarket receipt.

    Attributes:
        id: Unique identifier (UUID).
        image_path: Filesystem path to the uploaded receipt image.
        raw_text_lines: List[str] — raw OCR bounding-box text before parsing.
        items: Parsed FoodItem entities extracted from raw text.
        uploaded_at: Timestamp of initial upload.
        _state: Current lifecycle state (State Pattern).
        _state_handler: Active state handler implementing transitions.
        _failure_reason: Human-readable failure description (if any).
    """

    image_path: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    raw_text_lines: list[str] = field(default_factory=list)
    items: list[FoodItem] = field(default_factory=list)
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    _state: ReceiptState = field(default=ReceiptState.UPLOADED, repr=False)
    _state_handler: BaseReceiptState = field(
        default_factory=UploadedState, repr=False
    )
    _failure_reason: str | None = field(default=None, repr=False)

    # ─── State Transitions ────────────────────────────────

    def process(self) -> None:
        """Begin OCR processing."""
        self._state_handler.process(self)

    def mark_parsed(self) -> None:
        """Mark as successfully parsed."""
        self._state_handler.mark_parsed(self)

    def mark_failed(self, reason: str) -> None:
        """Mark as failed with a reason."""
        self._state_handler.mark_failed(self, reason)

    def complete(self) -> None:
        """Mark as fully completed."""
        self._state_handler.complete(self)

    # ─── Queries ──────────────────────────────────────────

    @property
    def state(self) -> ReceiptState:
        """Current lifecycle state."""
        return self._state

    @property
    def failure_reason(self) -> str | None:
        """Reason for failure, if applicable."""
        return self._failure_reason

    @property
    def is_terminal(self) -> bool:
        """Whether the receipt is in a terminal state."""
        return self._state in (ReceiptState.COMPLETED, ReceiptState.FAILED)
