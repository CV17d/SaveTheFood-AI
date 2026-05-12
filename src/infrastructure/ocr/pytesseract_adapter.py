"""
PyTesseract Adapter — Strategy Pattern concrete implementation.

Uses PyTesseract + OpenCV to extract text from receipt images.
This is the default OCR strategy for offline/local processing.

Data Structures Used:
    - List[str]: Raw bounding-box text arrays from OCR before parsing.
"""

from __future__ import annotations

from pathlib import Path

from ...domain.exceptions.domain_exceptions import OCRExtractionError
from ...domain.interfaces.ocr_provider_interface import OCRProviderInterface


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
            import numpy as np
            import pytesseract

            if self._tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = self._tesseract_cmd

            img = cv2.imread(str(image_path))
            
            # 1. Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 2. Denoise (filtro de mediana para eliminar ruido de sal y pimienta)
            denoised = cv2.medianBlur(gray, 3)
            
            # 3. Threshold adaptativo
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # 4. Deskew (Corrección de inclinación)
            coords = np.column_stack(np.where(thresh > 0))
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            (h, w) = thresh.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            deskewed = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            
            # 5. Crop de márgenes (eliminar bordes vacíos)
            # Encontrar contornos y hacer bounding box
            contours, _ = cv2.findContours(deskewed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                c = max(contours, key=cv2.contourArea)
                x, y, w_box, h_box = cv2.boundingRect(c)
                # Aplicar crop con un pequeño padding
                pad = 10
                y1 = max(0, y - pad)
                y2 = min(h, y + h_box + pad)
                x1 = max(0, x - pad)
                x2 = min(w, x + w_box + pad)
                processed_img = deskewed[y1:y2, x1:x2]
            else:
                processed_img = deskewed

            text = pytesseract.image_to_string(processed_img)
            return [line.strip() for line in text.split("\n") if line.strip()]

        except Exception as e:
            raise OCRExtractionError(f"PyTesseract extraction failed: {e}") from e

    def get_provider_name(self) -> str:
        return "PyTesseract (OpenCV)"
