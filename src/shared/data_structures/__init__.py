"""
Advanced Data Structures — SaveTheFood AI.

Custom implementations of fundamental data structures integrated
into the system architecture:

    - UndoStack (LIFO): Rollback/undo for manual OCR corrections.
    - ProcessingQueue (FIFO): Async receipt image processing pipeline.
    - ExpirationHeap (Min-Heap): Priority queue sorted by expiration date.
    - FoodCategoryTree (N-ary Tree): Hierarchical food categorization.
    - RecipeGraph (Bipartite Graph): Ingredient→Recipe recommendation engine.
    - ShelfLifeMap (Hashmap): O(1) shelf-life lookups.
"""

from src.shared.data_structures.undo_stack import UndoStack
from src.shared.data_structures.processing_queue import ProcessingQueue
from src.shared.data_structures.expiration_heap import ExpirationHeap
from src.shared.data_structures.food_category_tree import FoodCategoryTree
from src.shared.data_structures.recipe_graph import RecipeGraph
from src.shared.data_structures.shelf_life_map import ShelfLifeMap

__all__ = [
    "UndoStack",
    "ProcessingQueue",
    "ExpirationHeap",
    "FoodCategoryTree",
    "RecipeGraph",
    "ShelfLifeMap",
]
