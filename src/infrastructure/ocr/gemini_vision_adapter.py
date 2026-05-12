"""
Gemini Vision Adapter — Strategy Pattern concrete implementation.

Uses Gemini's multimodal vision API to extract text from receipt images.
This is the cloud-based OCR strategy for higher accuracy.
"""

from __future__ import annotations

from pathlib import Path

from src.domain.exceptions.domain_exceptions import OCRExtractionError
from src.domain.interfaces.ocr_provider_interface import OCRProviderInterface


class GeminiVisionAdapter(OCRProviderInterface):
    """
    Concrete OCR Strategy: Gemini Vision API.

    Sends the receipt image directly to Gemini's multimodal endpoint
    with a structured prompt to extract line items.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash") -> None:
        self._api_key = api_key
        self._model_name = model_name

    def extract_text(self, image_path: Path) -> list[str]:
        """
        Extract raw text lines from a receipt image using Gemini Vision.

        Args:
            image_path: Path to the receipt image.

        Returns:
            List[str]: Extracted text lines.

        Raises:
            OCRExtractionError: If the API call fails.
        """
        try:
            # TODO: Implement Gemini Vision multimodal extraction — Phase 2
            raise NotImplementedError("Gemini Vision extraction — Phase 2 deliverable.")

        except NotImplementedError:
            raise
        except Exception as e:
            raise OCRExtractionError(f"Gemini Vision extraction failed: {e}") from e

    def get_provider_name(self) -> str:
        return f"Gemini Vision ({self._model_name})"
