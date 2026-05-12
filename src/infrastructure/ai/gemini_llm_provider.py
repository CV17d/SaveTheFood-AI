"""
Gemini LLM Provider — concrete implementation of LLMProviderInterface.

Integrates with Google's Gemini API for:
    - RAG-powered recipe generation from expiring ingredients.
    - Shelf-life estimation as fallback for unknown food items.

This provider is typically wrapped by GeminiCacheProxy (Proxy Pattern).
"""

from __future__ import annotations

import json
import google.generativeai as genai
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
        genai.configure(api_key=self._api_key)
        self._model = genai.GenerativeModel(model_name)

    def generate_recipe(
        self, ingredients: list[str], constraints: dict[str, str] | None = None
    ) -> dict:
        """
        Generate a recipe using Gemini with RAG context.
        """
        prompt = f"""
        Eres un chef experto en cocina de aprovechamiento. 
        Genera una receta creativa utilizando exclusivamente estos ingredientes (puedes añadir básicos como sal, aceite, agua):
        {", ".join(ingredients)}

        Restricciones adicionales: {constraints if constraints else "Ninguna"}

        La respuesta DEBE ser un objeto JSON válido con la siguiente estructura:
        {{
            "title": "Nombre de la receta",
            "description": "Breve descripción del plato",
            "ingredients": ["ingrediente 1", "ingrediente 2"],
            "steps": ["paso 1", "paso 2"],
            "tags": ["tag1", "tag2"]
        }}
        """
        try:
            response = self._model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            raise RecipeGenerationError(f"Gemini API failed: {e}") from e

    def estimate_shelf_life(self, item_name: str) -> int:
        """
        Estimate shelf life via Gemini when item is not in the hashmap.
        Returns the estimated days of shelf life from purchase.
        """
        prompt = f"""
        Estima la vida útil promedio en días para el siguiente alimento desde el momento de su compra:
        '{item_name}'
        
        Responde ÚNICAMENTE con el número entero de días. Si no estás seguro, responde '7'.
        """
        try:
            response = self._model.generate_content(prompt)
            content = response.text.strip()
            # Try to extract the first number found in the text
            import re
            match = re.search(r'\d+', content)
            if match:
                return int(match.group())
            return 7  # Fallback
        except Exception:
            return 7  # Safe fallback for domain logic

    def get_provider_name(self) -> str:
        return f"Gemini ({self._model_name})"
