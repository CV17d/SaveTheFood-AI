"""
Application Constants.

Centralized configuration constants used across all layers.
"""

# ─── Application ──────────────────────────────────────────
APP_NAME = "SaveTheFood AI"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Intelligent food waste mitigation system"

# ─── OCR Strategies ───────────────────────────────────────
OCR_STRATEGY_PYTESSERACT = "pytesseract"
OCR_STRATEGY_GEMINI_VISION = "gemini_vision"

# ─── Urgency Thresholds (days) ────────────────────────────
URGENCY_CRITICAL_DAYS = 2
URGENCY_WARNING_DAYS = 5

# ─── Cache Defaults ──────────────────────────────────────
DEFAULT_CACHE_TTL_SECONDS = 3600
DEFAULT_CACHE_MAX_SIZE = 256

# ─── Dashboard ────────────────────────────────────────────
AVG_ITEM_COST_USD = 3.50
AVG_CO2_PER_ITEM_KG = 2.5
