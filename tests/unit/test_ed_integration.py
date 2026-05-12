"""Unit tests for integration of data structures in the processing pipeline."""

from __future__ import annotations

from datetime import date, timedelta
import pytest

from src.domain.entities.food_item import FoodItem
from src.domain.value_objects.expiration_date import ExpirationDate
from src.shared.data_structures.expiration_heap import ExpirationHeap
from src.shared.data_structures.shelf_life_map import ShelfLifeMap
from src.shared.data_structures.recipe_graph import RecipeGraph, RecipeNode
from src.shared.data_structures.food_category_tree import FoodCategoryTree
from src.shared.data_structures.processing_queue import ProcessingQueue

class TestEDIntegration:
    """Integration tests for Data Structures."""

    def test_shelf_life_to_expiration_integration(self) -> None:
        """Test: ShelfLifeMap lookup + ExpirationDate calculation produce correct dates."""
        shelf_map = ShelfLifeMap()
        item_name = "milk"
        purchase_date = date(2026, 5, 1)
        
        days = shelf_map.get(item_name)
        assert days == 7
        
        exp_vo = ExpirationDate.from_shelf_life(purchase_date, days)
        assert exp_vo.estimated_date == date(2026, 5, 8)
        assert exp_vo.confidence == "high"

    def test_expiration_heap_urgency_integration(self) -> None:
        """Test: ExpirationHeap extracts items in correct order of urgency."""
        heap: ExpirationHeap[FoodItem] = ExpirationHeap()
        
        item_critical = FoodItem(name="Chicken", expiration_date=date.today() + timedelta(days=1))
        item_warning = FoodItem(name="Milk", expiration_date=date.today() + timedelta(days=4))
        item_ok = FoodItem(name="Apple", expiration_date=date.today() + timedelta(days=10))
        
        # Insert in random order
        heap.insert(item_ok)
        heap.insert(item_critical)
        heap.insert(item_warning)
        
        extracted = heap.extract_top_n(3)
        assert extracted[0].name == "Chicken"
        assert extracted[1].name == "Milk"
        assert extracted[2].name == "Apple"

    def test_recipe_graph_coverage_integration(self) -> None:
        """Test: RecipeGraph.find_best_recipe() returns the recipe with most coverage."""
        graph = RecipeGraph()
        
        # Recipes
        graph.add_recipe(RecipeNode("r_pasta", "Pasta"))
        graph.add_recipe(RecipeNode("r_salad", "Salad"))
        
        # Edges
        graph.add_edge("tomato", "r_pasta")
        graph.add_edge("onion", "r_pasta")
        graph.add_edge("garlic", "r_pasta")
        
        graph.add_edge("tomato", "r_salad")
        graph.add_edge("lettuce", "r_salad")
        
        # Expiring ingredients
        expiring = ["tomato", "onion", "garlic"]
        
        best = graph.find_best_recipe(expiring)
        assert best == "r_pasta"  # 3 matches vs 1 match for salad

    def test_food_category_tree_hierarchy_integration(self) -> None:
        """Test: FoodCategoryTree.insert() + search() with real paths."""
        tree = FoodCategoryTree()
        paths = [
            ["Dairy", "Cheese", "Cheddar"],
            ["Dairy", "Milk"],
            ["Proteins", "Poultry", "Chicken"]
        ]
        
        for p in paths:
            tree.insert(p)
            
        assert tree.search(["Dairy", "Cheese", "Cheddar"]) is not None
        assert tree.search(["Dairy", "Milk"]) is not None
        assert tree.search(["Proteins"]) is not None
        
        # Check counts
        dairy_node = tree.search(["Dairy"])
        assert dairy_node.item_count == 2
        
    def test_processing_queue_fifo_integration(self) -> None:
        """Test: ProcessingQueue maintains FIFO order of receipts."""
        queue: ProcessingQueue[str] = ProcessingQueue()
        receipts = ["img1.jpg", "img2.jpg", "img3.jpg"]
        
        for r in receipts:
            queue.enqueue(r)
            
        assert queue.dequeue() == "img1.jpg"
        assert queue.dequeue() == "img2.jpg"
        assert queue.dequeue() == "img3.jpg"
