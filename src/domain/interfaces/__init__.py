"""Domain Interfaces (Ports) — contracts for the infrastructure layer."""

from src.domain.interfaces.llm_provider_interface import LLMProviderInterface
from src.domain.interfaces.ocr_provider_interface import OCRProviderInterface
from src.domain.interfaces.repository_interfaces import (
    FoodItemRepositoryInterface,
    ReceiptRepositoryInterface,
    RecipeRepositoryInterface,
)

__all__ = [
    "OCRProviderInterface",
    "LLMProviderInterface",
    "FoodItemRepositoryInterface",
    "ReceiptRepositoryInterface",
    "RecipeRepositoryInterface",
]
