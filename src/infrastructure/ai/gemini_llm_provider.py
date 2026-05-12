"""
Gemini LLM Provider — concrete implementation of LLMProviderInterface.

Integrates with Google's Gemini API for:
    - RAG-powered recipe generation from expiring ingredients.
    - Shelf-life estimation as fallback for unknown food items.

This provider is typically wrapped by GeminiCacheProxy (Proxy Pattern).
"""

from __future__ import annotations

from src.domain.exceptions.domain_exceptions import RecipeGenerationError
from src.domain.interfaces.llm_provider_interface import LLMProviderInterface


class GeminiLLMProvider(LLMProviderInterface):
    """
    Concrete LLM Provider: Google Gemini API.

    Handles prompt engineering, API communication, and response parsing.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash") -> None:
        self._api_key = api_key
        self._model_name = model_name
        # TODO: Initialize google.generativeai client — Phase 2

    def generate_recipe(
        self, ingredients: list[str], constraints: dict[str, str] | None = None
    ) -> dict:
        """
        Generate a recipe using Gemini with RAG context.

        TODO: Implement structured prompt + JSON response parsing — Phase 2.
        """
        try:
            raise NotImplementedError("Gemini recipe generation — Phase 2 deliverable.")
        except NotImplementedError:
            raise
        except Exception as e:
            raise RecipeGenerationError(f"Gemini API failed: {e}") from e

    def estimate_shelf_life(self, item_name: str) -> int:
        """
        Estimate shelf life via Gemini when item is not in the hashmap.

        TODO: Implement LLM-based estimation — Phase 2.
        """
        raise NotImplementedError("Gemini shelf-life estimation — Phase 2 deliverable.")

    def get_provider_name(self) -> str:
        return f"Gemini ({self._model_name})"
