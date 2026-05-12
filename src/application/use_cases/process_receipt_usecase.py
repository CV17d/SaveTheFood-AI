from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import ClassVar

from src.domain.entities.food_item import FoodItem
from src.domain.entities.receipt import Receipt
from src.domain.interfaces.llm_provider_interface import LLMProviderInterface
from src.domain.interfaces.ocr_provider_interface import OCRProviderInterface
from src.domain.interfaces.repository_interfaces import (
    FoodItemRepositoryInterface,
    ReceiptRepositoryInterface,
)
from src.domain.value_objects.expiration_date import ExpirationDate
from src.shared.data_structures.food_category_tree import FoodCategoryTree
from src.shared.data_structures.processing_queue import ProcessingQueue
from src.shared.data_structures.shelf_life_map import ShelfLifeMap
from src.shared.utils import normalize_food_name


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

    # Global mapping for categories — Deliverable 4
    CATEGORY_MAP: ClassVar[dict[str, list[str]]] = {
        "milk": ["Dairy", "Milk"],
        "cheese": ["Dairy", "Cheese"],
        "yogurt": ["Dairy", "Yogurt"],
        "butter": ["Dairy", "Butter"],
        "chicken": ["Proteins", "Poultry", "Chicken"],
        "beef": ["Proteins", "Red Meat", "Beef"],
        "pork": ["Proteins", "Red Meat", "Pork"],
        "fish": ["Proteins", "Seafood", "Fish"],
        "apple": ["Produce", "Fruits", "Apple"],
        "banana": ["Produce", "Fruits", "Banana"],
        "orange": ["Produce", "Fruits", "Orange"],
        "strawberry": ["Produce", "Fruits", "Strawberry"],
        "lettuce": ["Produce", "Vegetables", "Lettuce"],
        "tomato": ["Produce", "Vegetables", "Tomato"],
        "cucumber": ["Produce", "Vegetables", "Cucumber"],
        "carrot": ["Produce", "Vegetables", "Carrot"],
        "broccoli": ["Produce", "Vegetables", "Broccoli"],
        "potato": ["Produce", "Vegetables", "Potato"],
        "bread": ["Bakery", "Bread"],
        "eggs": ["Proteins", "Eggs"],
    }

    _queue: ClassVar[ProcessingQueue[str]] = ProcessingQueue()

    def __init__(
        self,
        ocr_provider: OCRProviderInterface,
        receipt_repo: ReceiptRepositoryInterface,
        food_item_repo: FoodItemRepositoryInterface,
        llm_provider: LLMProviderInterface | None = None,
        shelf_life_map: ShelfLifeMap | None = None,
        category_tree: FoodCategoryTree | None = None,
    ) -> None:
        self._ocr = ocr_provider
        self._receipt_repo = receipt_repo
        self._food_item_repo = food_item_repo
        self._llm = llm_provider
        self._shelf_life_map = shelf_life_map or ShelfLifeMap()
        self._category_tree = category_tree or FoodCategoryTree()

    def process_batch(self, image_paths: list[str]) -> list[ProcessReceiptResult]:
        """
        Process multiple receipts using the ProcessingQueue (FIFO).
        """
        for path in image_paths:
            self._queue.enqueue(path)
        
        results = []
        while not self._queue.is_empty:
            path = self._queue.dequeue()
            results.append(self.execute(path))
        return results

    def execute(self, image_path: str) -> ProcessReceiptResult:
        """
        Execute the receipt processing pipeline.
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
        """
        items: list[FoodItem] = []
        purchase_date = date.today()

        for line in raw_lines:
            raw_name = line.strip()
            if not raw_name:
                continue

            # 1. Normalize name
            normalized_name = normalize_food_name(raw_name)
            
            # 2. Category lookup
            category_path = self.CATEGORY_MAP.get(normalized_name.lower(), ["Uncategorized"])
            
            # 3. Shelf-life lookup (O(1)) — Deliverable 2
            shelf_life = self._shelf_life_map.get(normalized_name)
            source = "shelf_life_map"

            # 4. Fallback to LLM if not in map
            if shelf_life is None and self._llm:
                shelf_life = self._llm.estimate_shelf_life(normalized_name)
                source = "llm_estimate"
            
            # Default fallback if everything fails
            if shelf_life is None:
                shelf_life = 7
                source = "default"

            # 5. Calculate expiration date
            exp_vo = ExpirationDate.from_shelf_life(
                purchase_date=purchase_date,
                shelf_life_days=shelf_life,
                source=source
            )

            # 6. Create FoodItem
            item = FoodItem(
                name=normalized_name,
                receipt_id=receipt_id,
                purchase_date=purchase_date,
                expiration_date=exp_vo.estimated_date,
                category_path=category_path
            )

            # 7. Insert into FoodCategoryTree — Deliverable 4
            self._category_tree.insert(category_path)
            
            items.append(item)

        return items
