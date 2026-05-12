"""
GenerateRecipeUseCase — orchestrates recipe generation via RAG.

Flow:
    1. Query the Expiration Heap for the N most urgent items.
    2. Build a bipartite Ingredient→Recipe Graph query.
    3. Invoke LLM Provider (via Proxy cache) with prioritized ingredients.
    4. Construct Recipe entity via RecipeFactory.
    5. Persist and return.

Design Patterns Used:
    - Proxy Pattern: LLM calls are cached to reduce API quota usage.
    - Factory Pattern: RecipeFactory builds complex Recipe entities.

Data Structures Used:
    - Heap: Extract top-N most urgent expiring ingredients.
    - Graph (Bipartite): Connect ingredients to candidate recipes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from src.domain.entities.recipe import Recipe
from src.domain.interfaces.llm_provider_interface import LLMProviderInterface
from src.domain.interfaces.repository_interfaces import (
    FoodItemRepositoryInterface,
    RecipeRepositoryInterface,
)
from src.shared.data_structures.expiration_heap import ExpirationHeap
from src.shared.data_structures.recipe_graph import IngredientNode, RecipeGraph, RecipeNode


@dataclass
class GenerateRecipeResult:
    """DTO returned by the recipe generation use case."""

    recipe_id: str
    title: str
    ingredients_used: list[str]
    matched_expiring: int
    source: str = "llm"


class GenerateRecipeUseCase:
    """
    Application Use Case: generate recipes from expiring ingredients.
    """

    # Shared graph for reuse across use case instances if needed, 
    # but usually injected in a real DI container.
    _graph: ClassVar[RecipeGraph] = RecipeGraph()

    def __init__(
        self,
        llm_provider: LLMProviderInterface,
        food_item_repo: FoodItemRepositoryInterface,
        recipe_repo: RecipeRepositoryInterface,
        graph: RecipeGraph | None = None,
    ) -> None:
        self._llm = llm_provider
        self._food_item_repo = food_item_repo
        self._recipe_repo = recipe_repo
        self._graph = graph or self._graph

    def execute(
        self,
        max_ingredients: int = 10,
        expiring_within_days: int = 5,
        constraints: dict[str, str] | None = None,
    ) -> GenerateRecipeResult:
        """
        Generate a recipe prioritizing the most urgent expiring items.
        """
        # 1. Query expiring items from repository
        expiring_items = self._food_item_repo.find_expiring_within(expiring_within_days)
        
        # Fallback: If no urgent items, take any available items to avoid empty result
        if not expiring_items:
            expiring_items = self._food_item_repo.find_all()
            
        if not expiring_items:
            return GenerateRecipeResult("", "No hay ingredientes disponibles en el inventario", [], 0, "none")

        # 2. Use ExpirationHeap to prioritize (O(log N)) — Deliverable 3
        heap = ExpirationHeap()
        heap.build_from(expiring_items)
        top_items = heap.extract_top_n(max_ingredients)
        ingredient_names = [item.name for item in top_items]

        # 3. Check RecipeGraph for existing best match — Deliverable 5
        best_recipe_id = self._graph.find_best_recipe(ingredient_names)
        if best_recipe_id:
            existing_recipe = self._recipe_repo.find_by_id(best_recipe_id)
            if existing_recipe:
                return GenerateRecipeResult(
                    recipe_id=existing_recipe.id,
                    title=existing_recipe.title,
                    ingredients_used=existing_recipe.ingredients,
                    matched_expiring=existing_recipe.matched_expiring_count,
                    source="graph_cache"
                )

        # 4. Generate recipe via LLM (Proxy-cached)
        try:
            raw_recipe = self._llm.generate_recipe(ingredient_names, constraints)
            
            # 5. Build Recipe entity via Factory
            recipe = RecipeFactory.create(raw_recipe, matched_count=len(ingredient_names))

            # 6. Persist
            self._recipe_repo.save(recipe)

            # 7. Update RecipeGraph — Deliverable 5
            recipe_node = RecipeNode(recipe_id=recipe.id, title=recipe.title)
            self._graph.add_recipe(recipe_node)
            for ing in recipe.ingredients:
                self._graph.add_ingredient(IngredientNode(name=ing))
                self._graph.add_edge(ing, recipe.id)

            return GenerateRecipeResult(
                recipe_id=recipe.id,
                title=recipe.title,
                ingredients_used=ingredient_names,
                matched_expiring=recipe.matched_expiring_count,
                source="llm_generation"
            )
        except Exception as e:
            return GenerateRecipeResult(
                recipe_id="", 
                title=f"Error al generar receta: {str(e)}", 
                ingredients_used=ingredient_names, 
                matched_expiring=0, 
                source="error"
            )


class RecipeFactory:
    """
    Factory Pattern — constructs Recipe entities from raw LLM output.

    Centralizes the complex construction logic and validation
    that would otherwise clutter the use case.
    """

    @staticmethod
    def create(raw_data: dict, matched_count: int = 0) -> Recipe:
        """
        Build a validated Recipe entity from raw LLM response dict.

        Args:
            raw_data: Dictionary from LLM with recipe fields.
            matched_count: Number of expiring ingredients matched.

        Returns:
            Fully constructed Recipe domain entity.
        """
        return Recipe(
            title=raw_data.get("title", "Untitled Recipe"),
            description=raw_data.get("description", ""),
            ingredients=raw_data.get("ingredients", []),
            steps=raw_data.get("steps", []),
            estimated_time_minutes=raw_data.get("estimated_time_minutes", 30),
            servings=raw_data.get("servings", 2),
            tags=raw_data.get("tags", []),
            matched_expiring_count=matched_count,
            source="gemini_rag",
        )
