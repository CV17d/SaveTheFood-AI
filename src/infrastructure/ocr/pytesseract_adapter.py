"""
PyTesseract Adapter — Strategy Pattern concrete implementation.

Uses PyTesseract + OpenCV to extract text from receipt images.
This is the default OCR strategy for offline/local processing.

Data Structures Used:
    - List[str]: Raw bounding-box text arrays from OCR before parsing.
"""

from __future__ import annotations

from pathlib import Path

from src.domain.exceptions.domain_exceptions import OCRExtractionError
from src.domain.interfaces.ocr_provider_interface import OCRProviderInterface


class PyTesseractAdapter(OCRProviderInterface):
    """
    Concrete OCR Strategy: PyTesseract + OpenCV.

    Preprocessing pipeline:
        1. Load image via OpenCV.
        2. Convert to grayscale.
        3. Apply adaptive thresholding for receipt contrast.
        4. Extract text via PyTesseract.
        5. Split into bounding-box text lines (List[str]).
    """

    def __init__(self, tesseract_cmd: str | None = None) -> None:
        self._tesseract_cmd = tesseract_cmd

    def extract_text(self, image_path: Path) -> list[str]:
        """
        Extract raw text lines from a receipt image using PyTesseract.

        Args:
            image_path: Path to the receipt image.

        Returns:
            List[str]: Raw text lines (bounding-box level).

        Raises:
            OCRExtractionError: If extraction fails.
        """
        try:
            import cv2
            import pytesseract

            if self._tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = self._tesseract_cmd

            img = cv2.imread(str(image_path))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            text = pytesseract.image_to_string(thresh)
            return [line.strip() for line in text.split("\n") if line.strip()]

        except Exception as e:
            raise OCRExtractionError(f"PyTesseract extraction failed: {e}") from e

    def get_provider_name(self) -> str:
        return "PyTesseract (OpenCV)"
