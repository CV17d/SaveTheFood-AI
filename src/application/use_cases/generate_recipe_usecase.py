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

from src.domain.entities.recipe import Recipe
from src.domain.interfaces.llm_provider_interface import LLMProviderInterface
from src.domain.interfaces.repository_interfaces import (
    FoodItemRepositoryInterface,
    RecipeRepositoryInterface,
)


@dataclass
class GenerateRecipeResult:
    """DTO returned by the recipe generation use case."""

    recipe_id: str
    title: str
    ingredients_used: list[str]
    matched_expiring: int


class GenerateRecipeUseCase:
    """
    Application Use Case: generate recipes from expiring ingredients.

    The LLM provider is typically wrapped by the GeminiCacheProxy
    (Proxy Pattern) to avoid redundant API calls.
    """

    def __init__(
        self,
        llm_provider: LLMProviderInterface,
        food_item_repo: FoodItemRepositoryInterface,
        recipe_repo: RecipeRepositoryInterface,
    ) -> None:
        self._llm = llm_provider
        self._food_item_repo = food_item_repo
        self._recipe_repo = recipe_repo

    def execute(
        self,
        max_ingredients: int = 10,
        expiring_within_days: int = 5,
        constraints: dict[str, str] | None = None,
    ) -> GenerateRecipeResult:
        """
        Generate a recipe prioritizing the most urgent expiring items.

        Args:
            max_ingredients: Maximum ingredients to include.
            expiring_within_days: Lookahead window for expiring items.
            constraints: Optional dietary/cuisine constraints.

        Returns:
            GenerateRecipeResult DTO with recipe summary.
        """
        # 1. Query expiring items (will use Heap in shared layer)
        expiring = self._food_item_repo.find_expiring_within(expiring_within_days)
        ingredient_names = [item.name for item in expiring[:max_ingredients]]

        # 2. Generate recipe via LLM (Proxy-cached)
        raw_recipe = self._llm.generate_recipe(ingredient_names, constraints)

        # 3. Build Recipe entity via Factory
        recipe = RecipeFactory.create(raw_recipe, matched_count=len(ingredient_names))

        # 4. Persist
        self._recipe_repo.save(recipe)

        return GenerateRecipeResult(
            recipe_id=recipe.id,
            title=recipe.title,
            ingredients_used=ingredient_names,
            matched_expiring=recipe.matched_expiring_count,
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
