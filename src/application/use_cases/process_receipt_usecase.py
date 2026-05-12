"""
ProcessReceiptUseCase — orchestrates the full receipt ingestion pipeline.

Flow:
    1. Receive image path from presentation layer.
    2. Create Receipt entity (State: UPLOADED).
    3. Enqueue into the Processing Queue (FIFO).
    4. Dequeue and invoke OCR Strategy (extract raw text lines → List[str]).
    5. Parse raw lines into FoodItem entities.
    6. Estimate expiration dates via shelf-life Hashmap + LLM fallback.
    7. Insert FoodItems into the Expiration Heap (Priority Queue).
    8. Insert FoodItems into the Food Category Tree.
    9. Persist via Repository.
    10. Transition Receipt state: PROCESSING → PARSED → COMPLETED.

Design Patterns Used:
    - Strategy Pattern: OCR provider selection (PyTesseract vs. Gemini Vision).
    - State Pattern: Receipt lifecycle transitions.
    - Factory Pattern: ReceiptFactory for complex entity construction.

Data Structures Used:
    - Queue (FIFO): Async processing pipeline for uploaded images.
    - List: Raw OCR bounding-box text storage.
    - Dictionary/Hashmap: O(1) shelf-life lookups.
    - Heap: Priority queue for expiring items.
    - Trie/Tree: Food category insertion.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.domain.entities.food_item import FoodItem
from src.domain.entities.receipt import Receipt
from src.domain.interfaces.ocr_provider_interface import OCRProviderInterface
from src.domain.interfaces.repository_interfaces import (
    FoodItemRepositoryInterface,
    ReceiptRepositoryInterface,
)


@dataclass
class ProcessReceiptResult:
    """DTO returned by the use case."""

    receipt_id: str
    items_extracted: int
    state: str
    errors: list[str]


class ProcessReceiptUseCase:
    """
    Application Use Case: process a receipt image end-to-end.

    Depends ONLY on domain interfaces (ports), never on concrete
    infrastructure classes. Injected via the DI container.
    """

    def __init__(
        self,
        ocr_provider: OCRProviderInterface,
        receipt_repo: ReceiptRepositoryInterface,
        food_item_repo: FoodItemRepositoryInterface,
    ) -> None:
        self._ocr = ocr_provider
        self._receipt_repo = receipt_repo
        self._food_item_repo = food_item_repo

    def execute(self, image_path: str) -> ProcessReceiptResult:
        """
        Execute the receipt processing pipeline.

        Args:
            image_path: Filesystem path to the receipt image.

        Returns:
            ProcessReceiptResult DTO with extraction summary.
        """
        # 1. Create Receipt entity (State: UPLOADED)
        receipt = Receipt(image_path=image_path)

        # 2. Transition to PROCESSING
        receipt.process()

        try:
            # 3. Extract raw text via OCR Strategy
            raw_lines: list[str] = self._ocr.extract_text(Path(image_path))
            receipt.raw_text_lines = raw_lines

            # 4. Parse raw lines into FoodItems
            items = self._parse_items(raw_lines, receipt.id)

            # 5. Attach items and transition to PARSED
            receipt.items = items
            receipt.mark_parsed()

            # 6. Persist
            self._receipt_repo.save(receipt)
            self._food_item_repo.save_batch(items)

            # 7. Transition to COMPLETED
            receipt.complete()

            return ProcessReceiptResult(
                receipt_id=receipt.id,
                items_extracted=len(items),
                state=receipt.state.name,
                errors=[],
            )

        except Exception as e:
            receipt.mark_failed(str(e))
            self._receipt_repo.save(receipt)
            return ProcessReceiptResult(
                receipt_id=receipt.id,
                items_extracted=0,
                state=receipt.state.name,
                errors=[str(e)],
            )

    def _parse_items(self, raw_lines: list[str], receipt_id: str) -> list[FoodItem]:
        """
        Parse raw OCR text lines into FoodItem entities.

        TODO: Implement NLP-based parsing logic in Phase 1.
        """
        items: list[FoodItem] = []
        for line in raw_lines:
            cleaned = line.strip()
            if cleaned:
                items.append(FoodItem(name=cleaned, receipt_id=receipt_id))
        return items
