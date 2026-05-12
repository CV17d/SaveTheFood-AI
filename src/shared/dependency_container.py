"""
Dependency Injection Container.

Maps domain interfaces (ports) to concrete infrastructure implementations
(adapters). This is the ONLY place where concrete classes are imported
and wired together, ensuring the Dependency Rule is never violated
in application or domain code.

Strategy Pattern Selection:
    OCR_STRATEGY env var → selects PyTesseractAdapter or GeminiVisionAdapter.

Proxy Pattern Wiring:
    GeminiLLMProvider is wrapped by GeminiCacheProxy before injection.
"""

from __future__ import annotations

from ..domain.interfaces.llm_provider_interface import LLMProviderInterface
from ..domain.interfaces.ocr_provider_interface import OCRProviderInterface
from ..domain.interfaces.repository_interfaces import (
    FoodItemRepositoryInterface,
    ReceiptRepositoryInterface,
    RecipeRepositoryInterface,
)
from ..infrastructure.ai.gemini_cache_proxy import GeminiCacheProxy
from ..infrastructure.ai.gemini_llm_provider import GeminiLLMProvider
from ..infrastructure.ocr.gemini_vision_adapter import GeminiVisionAdapter
from ..infrastructure.ocr.pytesseract_adapter import PyTesseractAdapter
from ..infrastructure.persistence.database_session import DatabaseSession
from ..infrastructure.persistence.sqlalchemy_food_repository import SQLAlchemyFoodRepository
from ..infrastructure.persistence.sqlalchemy_receipt_repository import SQLAlchemyReceiptRepository
from ..infrastructure.persistence.sqlalchemy_recipe_repository import SQLAlchemyRecipeRepository
from .constants import (
    DEFAULT_CACHE_MAX_SIZE,
    DEFAULT_CACHE_TTL_SECONDS,
    OCR_STRATEGY_GEMINI_VISION,
)


class DependencyContainer:
    """
    Composition Root — wires all dependencies for the application.

    Usage:
        container = DependencyContainer(settings)
        ocr = container.ocr_provider()
        llm = container.llm_provider()  # Returns cached proxy
    """

    def __init__(
        self,
        database_url: str = "sqlite:///data/db/savethefood.db",
        ocr_strategy: str = "pytesseract",
        gemini_api_key: str = "",
        gemini_model: str = "gemini-2.0-flash",
        tesseract_cmd: str | None = None,
        cache_ttl: int = DEFAULT_CACHE_TTL_SECONDS,
        cache_max_size: int = DEFAULT_CACHE_MAX_SIZE,
    ) -> None:
        self._database_url = database_url
        self._ocr_strategy = ocr_strategy
        self._gemini_api_key = gemini_api_key
        self._gemini_model = gemini_model
        self._tesseract_cmd = tesseract_cmd
        self._cache_ttl = cache_ttl
        self._cache_max_size = cache_max_size

        # Singleton instances
        self._db_session: DatabaseSession | None = None
        self._ocr: OCRProviderInterface | None = None
        self._llm: LLMProviderInterface | None = None

    # ─── Database ─────────────────────────────────────────

    def db_session(self) -> DatabaseSession:
        if self._db_session is None:
            self._db_session = DatabaseSession(self._database_url)
        return self._db_session

    # ─── OCR Strategy Selection ───────────────────────────

    def ocr_provider(self) -> OCRProviderInterface:
        if self._ocr is None:
            if self._ocr_strategy == OCR_STRATEGY_GEMINI_VISION:
                self._ocr = GeminiVisionAdapter(
                    api_key=self._gemini_api_key,
                    model_name=self._gemini_model,
                )
            else:
                self._ocr = PyTesseractAdapter(
                    tesseract_cmd=self._tesseract_cmd,
                )
        return self._ocr

    # ─── LLM Provider (Proxy-Wrapped) ─────────────────────

    def llm_provider(self) -> LLMProviderInterface:
        if self._llm is None:
            real = GeminiLLMProvider(
                api_key=self._gemini_api_key,
                model_name=self._gemini_model,
            )
            self._llm = GeminiCacheProxy(
                real_provider=real,
                ttl_seconds=self._cache_ttl,
                max_size=self._cache_max_size,
            )
        return self._llm

    # ─── Repositories ─────────────────────────────────────

    def food_item_repository(self) -> FoodItemRepositoryInterface:
        return SQLAlchemyFoodRepository(self.db_session())

    def receipt_repository(self) -> ReceiptRepositoryInterface:
        return SQLAlchemyReceiptRepository(self.db_session())

    def recipe_repository(self) -> RecipeRepositoryInterface:
        return SQLAlchemyRecipeRepository(self.db_session())
