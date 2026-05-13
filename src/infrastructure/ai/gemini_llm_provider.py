"""
Gemini LLM Provider — concrete implementation of LLMProviderInterface.

Integrates with Google's Gemini API for:
    - RAG-powered recipe generation from expiring ingredients.
    - Shelf-life estimation as fallback for unknown food items.

This provider is typically wrapped by GeminiCacheProxy (Proxy Pattern).
"""

from __future__ import annotations

import json
import logging
import re
import google.generativeai as genai
from src.domain.exceptions.domain_exceptions import RecipeGenerationError
from src.domain.interfaces.llm_provider_interface import LLMProviderInterface

logger = logging.getLogger(__name__)

class GeminiLLMProvider(LLMProviderInterface):
    """
    Concrete LLM Provider: Google Gemini API.

    Handles prompt engineering, API communication, and response parsing.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash") -> None:
        self._api_key = api_key
        self._model_name = model_name
        genai.configure(api_key=self._api_key)
        self._model = genai.GenerativeModel(self._model_name)

    def generate_recipe(
        self, ingredients: list[str], constraints: dict[str, str] | None = None
    ) -> dict:
        """
        Generate a recipe using Gemini with RAG context.
        """
        system_prompt = (
            "Eres un chef experto especializado en reducir el desperdicio de alimentos (Zero Waste Chef). "
            "Tu objetivo es crear recetas deliciosas utilizando ingredientes que están a punto de vencer. "
            "IMPORTANTE: Toda la respuesta (título, descripción, ingredientes, pasos y etiquetas) DEBE ESTAR EN ESPAÑOL. "
            "Responde ÚNICAMENTE en formato JSON válido."
        )
        
        ingredients_str = ", ".join(ingredients)
        constraints_str = json.dumps(constraints) if constraints else "Ninguna"
        
        prompt = (
            f"{system_prompt}\n\n"
            f"Ingredientes disponibles: {ingredients_str}\n"
            f"Restricciones: {constraints_str}\n\n"
            "Genera una receta que maximice el uso de estos ingredientes. "
            "La respuesta JSON debe tener exactamente estas llaves en español:\n"
            "{\n"
            "  \"title\": \"título de la receta\",\n"
            "  \"description\": \"breve descripción\",\n"
            "  \"ingredients\": [\"lista de ingredientes con cantidades\"],\n"
            "  \"steps\": [\"pasos detallados de la preparación\"],\n"
            "  \"estimated_time_minutes\": int,\n"
            "  \"servings\": int,\n"
            "  \"tags\": [\"etiquetas como 'rápido', 'saludable', etc.\"]\n"
            "}"
        )

        try:
            response = self._model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                ),
            )
            content = response.text.strip()
            
            # Clean JSON if it's wrapped in markdown blocks
            if content.startswith("```json"):
                content = content.replace("```json", "", 1).replace("```", "", 1).strip()
            elif content.startswith("```"):
                content = content.replace("```", "", 2).strip()

            try:
                recipe_data = json.loads(content)
                return recipe_data
            except json.JSONDecodeError:
                # Attempt to find JSON block with regex if direct parsing fails
                match = re.search(r"\{.*\}", content, re.DOTALL)
                if match:
                    return json.loads(match.group())
                raise RecipeGenerationError("Failed to parse JSON from Gemini response.")
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise RecipeGenerationError(f"Gemini API failed: {e}") from e

    def estimate_shelf_life(self, item_name: str) -> int:
        """
        Estimate shelf life via Gemini when item is not in the hashmap.
        """
        prompt = (
            f"How many days does '{item_name}' typically last after being purchased from a supermarket? "
            "Respond ONLY with a single integer representing the number of days. "
            "If unsure, provide a conservative estimate."
        )

        try:
            response = self._model.generate_content(prompt)
            content = response.text.strip()
            
            # Extract numbers from response
            numbers = re.findall(r"\d+", content)
            if numbers:
                return int(numbers[0])
            
            logger.warning(f"Could not extract shelf life for '{item_name}' from response: {content}")
            return 7  # Default fallback
        except Exception as e:
            logger.error(f"Error estimating shelf life for '{item_name}': {e}")
            return 7  # Default fallback

    def get_provider_name(self) -> str:
        return f"Gemini ({self._model_name})"
