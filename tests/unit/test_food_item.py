"""Unit tests for FoodItem entity and data structures."""

from __future__ import annotations

import pytest
from datetime import date, timedelta

from src.domain.entities.food_item import FoodItem
from src.shared.data_structures.expiration_heap import ExpirationHeap
from src.shared.data_structures.shelf_life_map import ShelfLifeMap
from src.shared.data_structures.undo_stack import UndoStack
from src.shared.data_structures.processing_queue import ProcessingQueue
from src.shared.data_structures.food_category_tree import FoodCategoryTree
from src.shared.data_structures.recipe_graph import RecipeGraph, IngredientNode, RecipeNode


class TestFoodItem:
    """Tests for FoodItem entity domain logic."""

    def test_days_until_expiration_positive(self) -> None:
        item = FoodItem(name="Milk", expiration_date=date.today() + timedelta(days=5))
        assert item.days_until_expiration == 5

    def test_is_expired(self) -> None:
        item = FoodItem(name="Bread", expiration_date=date.today() - timedelta(days=1))
        assert item.is_expired is True

    def test_urgency_critical(self) -> None:
        item = FoodItem(name="Chicken", expiration_date=date.today() + timedelta(days=1))
        assert item.urgency_level == "CRITICAL"

    def test_heap_ordering(self) -> None:
        early = FoodItem(name="A", expiration_date=date.today() + timedelta(days=1))
        late = FoodItem(name="B", expiration_date=date.today() + timedelta(days=10))
        assert early < late


class TestExpirationHeap:
    """Tests for the min-heap priority queue."""

    def test_insert_and_extract(self) -> None:
        heap: ExpirationHeap[FoodItem] = ExpirationHeap()
        late = FoodItem(name="Apple", expiration_date=date.today() + timedelta(days=10))
        early = FoodItem(name="Milk", expiration_date=date.today() + timedelta(days=1))
        heap.insert(late)
        heap.insert(early)
        assert heap.extract_min().name == "Milk"

    def test_extract_top_n(self) -> None:
        heap: ExpirationHeap[FoodItem] = ExpirationHeap()
        for i in range(5):
            heap.insert(FoodItem(name=f"Item{i}", expiration_date=date.today() + timedelta(days=i)))
        top3 = heap.extract_top_n(3)
        assert len(top3) == 3


class TestShelfLifeMap:
    """Tests for the hashmap shelf-life lookups."""

    def test_known_item(self) -> None:
        m = ShelfLifeMap()
        assert m.get("milk") == 7

    def test_unknown_item(self) -> None:
        m = ShelfLifeMap()
        assert m.get("dragon fruit") is None

    def test_case_insensitive(self) -> None:
        m = ShelfLifeMap()
        assert m.get("MILK") == 7


class TestUndoStack:
    """Tests for the LIFO undo stack."""

    def test_push_pop(self) -> None:
        stack: UndoStack[str] = UndoStack()
        stack.push("a")
        stack.push("b")
        assert stack.pop() == "b"
        assert stack.pop() == "a"

    def test_empty_pop_raises(self) -> None:
        stack: UndoStack[str] = UndoStack()
        with pytest.raises(IndexError):
            stack.pop()


class TestProcessingQueue:
    """Tests for the FIFO processing queue."""

    def test_fifo_order(self) -> None:
        q: ProcessingQueue[str] = ProcessingQueue()
        q.enqueue("first")
        q.enqueue("second")
        assert q.dequeue() == "first"


class TestFoodCategoryTree:
    """Tests for the N-ary category tree."""

    def test_insert_and_search(self) -> None:
        tree = FoodCategoryTree()
        tree.insert(["Dairy", "Cheese", "Cheddar"])
        node = tree.search(["Dairy", "Cheese", "Cheddar"])
        assert node is not None
        assert node.name == "Cheddar"

    def test_get_children(self) -> None:
        tree = FoodCategoryTree()
        tree.insert(["Dairy", "Milk"])
        tree.insert(["Dairy", "Cheese"])
        children = tree.get_children(["Dairy"])
        assert "Milk" in children
        assert "Cheese" in children


class TestRecipeGraph:
    """Tests for the bipartite ingredient-recipe graph."""

    def test_find_best_recipe(self) -> None:
        g = RecipeGraph()
        g.add_recipe(RecipeNode("r1", "Salad"))
        g.add_recipe(RecipeNode("r2", "Soup"))
        g.add_edge("lettuce", "r1")
        g.add_edge("tomato", "r1")
        g.add_edge("tomato", "r2")
        g.add_edge("onion", "r2")

        best = g.find_best_recipe(["lettuce", "tomato"])
        assert best == "r1"  # r1 has 2 matches vs r2's 1
