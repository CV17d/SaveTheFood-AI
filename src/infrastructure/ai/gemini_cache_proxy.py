"""
Gemini Cache Proxy — Proxy Pattern for caching LLM API calls.

Wraps GeminiLLMProvider to intercept calls and serve cached results
when identical ingredient sets are queried. Reduces API quota usage
and latency by avoiding redundant LLM invocations.

Data Structures Used:
    - Dictionary/Hashmap: O(1) cache lookup by frozen ingredient set key.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

from src.domain.interfaces.llm_provider_interface import LLMProviderInterface


@dataclass
class CacheEntry:
    """Single cache entry with TTL tracking."""

    value: dict | int
    created_at: float
    ttl_seconds: float

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl_seconds


class GeminiCacheProxy(LLMProviderInterface):
    """
    Proxy Pattern: caching wrapper around any LLMProviderInterface.

    Intercepts generate_recipe() and estimate_shelf_life() calls,
    computing a deterministic cache key from the input parameters.
    On cache hit, returns the stored result immediately (O(1) lookup).
    On cache miss, delegates to the real provider and stores the result.

    Attributes:
        _real_provider: The actual LLM provider being proxied.
        _cache: Dictionary/Hashmap for O(1) cached result lookups.
        _ttl_seconds: Time-to-live for cache entries.
        _max_size: Maximum cache entries before eviction.
    """

    def __init__(
        self,
        real_provider: LLMProviderInterface,
        ttl_seconds: int = 3600,
        max_size: int = 256,
    ) -> None:
        self._real_provider = real_provider
        self._cache: dict[str, CacheEntry] = {}
        self._ttl_seconds = ttl_seconds
        self._max_size = max_size

    def generate_recipe(
        self, ingredients: list[str], constraints: dict[str, str] | None = None
    ) -> dict:
        """Cache-aware recipe generation."""
        cache_key = self._build_key("recipe", ingredients, constraints)

        # Cache HIT
        entry = self._cache.get(cache_key)
        if entry is not None and not entry.is_expired:
            return entry.value  # type: ignore[return-value]

        # Cache MISS — delegate to real provider
        result = self._real_provider.generate_recipe(ingredients, constraints)
        self._store(cache_key, result)
        return result

    def estimate_shelf_life(self, item_name: str) -> int:
        """Cache-aware shelf-life estimation."""
        cache_key = self._build_key("shelf", [item_name])

        entry = self._cache.get(cache_key)
        if entry is not None and not entry.is_expired:
            return entry.value  # type: ignore[return-value]

        result = self._real_provider.estimate_shelf_life(item_name)
        self._store(cache_key, result)
        return result

    def get_provider_name(self) -> str:
        return f"CacheProxy({self._real_provider.get_provider_name()})"

    # ─── Private Helpers ──────────────────────────────────

    def _build_key(
        self, prefix: str, items: list[str], extra: dict | None = None
    ) -> str:
        """Build a deterministic cache key from inputs."""
        normalized = sorted(i.lower().strip() for i in items)
        payload = {"prefix": prefix, "items": normalized, "extra": extra or {}}
        raw = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _store(self, key: str, value: dict | int) -> None:
        """Store a result in cache, evicting oldest if at capacity."""
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._cache, key=lambda k: self._cache[k].created_at)
            del self._cache[oldest_key]
        self._cache[key] = CacheEntry(
            value=value, created_at=time.time(), ttl_seconds=self._ttl_seconds
        )

    @property
    def cache_size(self) -> int:
        """Current number of cached entries."""
        return len(self._cache)

    def clear_cache(self) -> None:
        """Flush the entire cache."""
        self._cache.clear()
