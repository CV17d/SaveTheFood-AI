"""
OCR Provider Interface — Strategy Pattern Port.

Defines the contract that all OCR adapters must implement.
Concrete strategies: PyTesseractAdapter, GeminiVisionAdapter.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class OCRProviderInterface(ABC):
    """
    Abstract interface for OCR text extraction.

    Implements the Strategy Pattern: the application layer programs
    against this interface, and the infrastructure layer provides
    concrete implementations (PyTesseract, Gemini Vision).
    """

    @abstractmethod
    def extract_text(self, image_path: Path) -> list[str]:
        """
        Extract raw text lines from a receipt image.

        Args:
            image_path: Path to the receipt image file.

        Returns:
            List[str]: Raw bounding-box text lines before parsing.

        Raises:
            OCRExtractionError: If text extraction fails.
        """
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of this OCR provider for logging."""
        ...
