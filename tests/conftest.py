"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import pytest

from src.domain.entities.food_item import FoodItem
from src.domain.entities.receipt import Receipt
from src.shared.data_structures.shelf_life_map import ShelfLifeMap


@pytest.fixture
def sample_receipt() -> Receipt:
    """Create a sample receipt for testing."""
    return Receipt(image_path="/tmp/test_receipt.jpg")


@pytest.fixture
def sample_food_items() -> list[FoodItem]:
    """Create a list of sample food items."""
    from datetime import date, timedelta

    return [
        FoodItem(name="Milk", expiration_date=date.today() + timedelta(days=2)),
        FoodItem(name="Chicken", expiration_date=date.today() + timedelta(days=1)),
        FoodItem(name="Apple", expiration_date=date.today() + timedelta(days=14)),
        FoodItem(name="Bread", expiration_date=date.today() - timedelta(days=1)),
    ]


@pytest.fixture
def shelf_life_map() -> ShelfLifeMap:
    """Create a shelf-life map fixture."""
    return ShelfLifeMap()
