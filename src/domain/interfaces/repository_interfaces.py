"""
Repository Interfaces — Ports for data persistence.

These interfaces define the contracts that infrastructure repositories
must implement. The domain layer NEVER depends on SQLAlchemy or any ORM.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.food_item import FoodItem
from src.domain.entities.receipt import Receipt
from src.domain.entities.recipe import Recipe


class ReceiptRepositoryInterface(ABC):
    """Port for Receipt persistence operations."""

    @abstractmethod
    def save(self, receipt: Receipt) -> None: ...

    @abstractmethod
    def find_by_id(self, receipt_id: str) -> Receipt | None: ...

    @abstractmethod
    def find_all(self) -> list[Receipt]: ...

    @abstractmethod
    def delete(self, receipt_id: str) -> None: ...


class FoodItemRepositoryInterface(ABC):
    """Port for FoodItem persistence operations."""

    @abstractmethod
    def save(self, item: FoodItem) -> None: ...

    @abstractmethod
    def save_batch(self, items: list[FoodItem]) -> None: ...

    @abstractmethod
    def find_by_id(self, item_id: str) -> FoodItem | None: ...

    @abstractmethod
    def find_all(self) -> list[FoodItem]: ...

    @abstractmethod
    def find_expiring_within(self, days: int) -> list[FoodItem]: ...

    @abstractmethod
    def delete(self, item_id: str) -> None: ...


class RecipeRepositoryInterface(ABC):
    """Port for Recipe persistence operations."""

    @abstractmethod
    def save(self, recipe: Recipe) -> None: ...

    @abstractmethod
    def find_by_id(self, recipe_id: str) -> Recipe | None: ...

    @abstractmethod
    def find_all(self) -> list[Recipe]: ...

    @abstractmethod
    def find_by_ingredient(self, ingredient: str) -> list[Recipe]: ...
