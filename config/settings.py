"""
Application Settings — Pydantic-based environment configuration.

Loads settings from .env file and environment variables with validation.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Gemini API
    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-2.0-flash"

    # Database
    database_url: str = "sqlite:///data/db/savethefood.db"

    # OCR
    ocr_strategy: str = "pytesseract"
    tesseract_cmd_path: str = "/usr/bin/tesseract"

    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    debug: bool = True

    # Cache
    cache_ttl_seconds: int = 3600
    cache_max_size: int = 256

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
