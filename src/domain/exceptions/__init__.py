"""Domain Exceptions — custom error hierarchy."""

from src.domain.exceptions.domain_exceptions import (
    DomainException,
    EntityNotFoundError,
    InvalidReceiptError,
    OCRExtractionError,
    RecipeGenerationError,
    ShelfLifeNotFoundError,
)

__all__ = [
    "DomainException",
    "EntityNotFoundError",
    "InvalidReceiptError",
    "OCRExtractionError",
    "RecipeGenerationError",
    "ShelfLifeNotFoundError",
]
