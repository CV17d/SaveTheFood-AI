"""
Domain Exceptions.

All custom exceptions inherit from DomainException to allow
infrastructure layers to catch domain-level errors uniformly.
"""

from __future__ import annotations


class DomainException(Exception):
    """Base exception for all domain-level errors."""

    def __init__(self, message: str = "A domain error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(DomainException):
    """Raised when a requested entity does not exist in the repository."""

    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(f"{entity_type} with id '{entity_id}' not found.")


class InvalidReceiptError(DomainException):
    """Raised when a receipt fails validation (corrupt image, unreadable, etc.)."""

    pass


class OCRExtractionError(DomainException):
    """Raised when the OCR engine fails to extract text from an image."""

    pass


class RecipeGenerationError(DomainException):
    """Raised when the LLM fails to generate a valid recipe."""

    pass


class ShelfLifeNotFoundError(DomainException):
    """Raised when a food item has no known shelf-life entry in the hashmap."""

    def __init__(self, item_name: str) -> None:
        super().__init__(
            f"No shelf-life data found for '{item_name}'. "
            "Consider adding it to the shelf-life map or using LLM estimation."
        )
