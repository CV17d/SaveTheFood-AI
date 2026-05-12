"""
LLM Provider Interface — Port for AI/RAG operations.

Defines the contract for all LLM adapters (Gemini, etc.).
The Proxy Pattern wraps this interface to add caching.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProviderInterface(ABC):
    """
    Abstract interface for LLM-powered operations.

    Used by: GeminiLLMProvider (direct), GeminiCacheProxy (cached wrapper).
    """

    @abstractmethod
    def generate_recipe(
        self, ingredients: list[str], constraints: dict[str, str] | None = None
    ) -> dict:
        """
        Generate a recipe from a list of ingredients.

        Args:
            ingredients: List of ingredient names to use.
            constraints: Optional dietary/cuisine constraints.

        Returns:
            Dict with keys: title, description, ingredients, steps, tags.

        Raises:
            RecipeGenerationError: If the LLM fails.
        """
        ...

    @abstractmethod
    def estimate_shelf_life(self, item_name: str) -> int:
        """
        Estimate shelf life in days for a food item via LLM.

        Used as fallback when the item is not in the shelf-life hashmap.

        Args:
            item_name: Name of the food item.

        Returns:
            Estimated shelf life in days.
        """
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of this LLM provider for logging."""
        ...
