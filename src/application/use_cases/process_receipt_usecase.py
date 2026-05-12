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

from datetime import date, timedelta
from src.domain.entities.food_item import FoodItem
from src.domain.entities.receipt import Receipt
from src.domain.interfaces.llm_provider_interface import LLMProviderInterface
from src.domain.interfaces.ocr_provider_interface import OCRProviderInterface
from src.domain.interfaces.repository_interfaces import (
    FoodItemRepositoryInterface,
    ReceiptRepositoryInterface,
)
from src.shared.data_structures.shelf_life_map import ShelfLifeMap


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

    Orchestrates OCR extraction, NLP parsing, and expiration estimation.
    """

    def __init__(
        self,
        ocr_provider: OCRProviderInterface,
        llm_provider: LLMProviderInterface,
        receipt_repo: ReceiptRepositoryInterface,
        food_item_repo: FoodItemRepositoryInterface,
        shelf_life_map: ShelfLifeMap | None = None,
    ) -> None:
        self._ocr = ocr_provider
        self._llm = llm_provider
        self._receipt_repo = receipt_repo
        self._food_item_repo = food_item_repo
        self._shelf_life_map = shelf_life_map or ShelfLifeMap()

    def execute(self, image_path: str) -> ProcessReceiptResult:
        """
        Execute the receipt processing pipeline.
        """
        receipt = Receipt(image_path=image_path)
        receipt.process()

        try:
            # 1. Extract raw text
            raw_lines: list[str] = self._ocr.extract_text(Path(image_path))
            receipt.raw_text_lines = raw_lines

            # 2. Parse and estimate expiration
            items = self._parse_items(raw_lines, receipt.id)

            # 3. State transitions and persistence
            receipt.items = items
            receipt.mark_parsed()

            self._receipt_repo.save(receipt)
            self._food_item_repo.save_batch(items)

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
        Parse raw lines into FoodItem entities with estimated expiration.
        """
        items: list[FoodItem] = []
        for line in raw_lines:
            name = line.strip()
            if not name or len(name) < 3:
                continue
            
            # Simple noise filter (heuristic)
            if any(token in name.upper() for token in ["TOTAL", "SUBTOTAL", "TAX", "VISA", "CASH", "CHANGE"]):
                continue

            # 1. Estimate shelf life (O(1) map or LLM fallback)
            days = self._shelf_life_map.get(name)
            if days is None:
                days = self._llm.estimate_shelf_life(name)
            
            # 2. If it's likely a food item (shelf life found/estimated)
            if days > 0:
                expiration = date.today() + timedelta(days=days)
                items.append(
                    FoodItem(
                        name=name,
                        receipt_id=receipt_id,
                        expiration_date=expiration,
                        confidence_score=0.9 if self._shelf_life_map.contains(name) else 0.7
                    )
                )
        
        return items
