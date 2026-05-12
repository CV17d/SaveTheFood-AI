# 🔌 Infrastructure Layer — Adaptadores Concretos

> **Responsabilidad:** Implementar los contratos (Ports) definidos en Domain.
> Esta capa contiene TODO el código que depende de frameworks, APIs externas,
> y bases de datos.

## Responsabilidades

1. **OCR Adapters** — Implementaciones concretas del Strategy Pattern para extracción de texto.
2. **AI Providers** — Adaptadores para LLMs (Gemini) con Proxy Pattern para caching.
3. **Persistence** — SQLAlchemy ORM, modelos de base de datos, y repositorios concretos.

## Patrones de Diseño en Esta Capa

| Patrón | Archivo | Descripción |
|--------|---------|-------------|
| **Strategy Pattern** | `ocr/pytesseract_adapter.py`, `ocr/gemini_vision_adapter.py` | OCR intercambiable por env var |
| **Proxy Pattern** | `ai/gemini_cache_proxy.py` wraps `ai/gemini_llm_provider.py` | Cache O(1) con TTL + eviction |
| **Repository Pattern** | `persistence/sqlalchemy_food_repository.py` | Abstrae SQLAlchemy detrás de interfaz |

## Estructura de Archivos

```
infrastructure/
├── __init__.py
├── ocr/
│   ├── __init__.py
│   ├── pytesseract_adapter.py     ← Strategy: OpenCV + Tesseract (local)
│   └── gemini_vision_adapter.py   ← Strategy: Gemini Vision API (cloud)
├── ai/
│   ├── __init__.py
│   ├── gemini_llm_provider.py     ← Proveedor LLM real (API calls)
│   └── gemini_cache_proxy.py      ← Proxy con hashmap cache O(1)
└── persistence/
    ├── __init__.py
    ├── database_session.py        ← SQLAlchemy engine + session factory
    ├── models.py                  ← ORM models (receipts, food_items, recipes)
    └── sqlalchemy_food_repository.py ← Repository con entity↔model mappers
```

## Estado de Implementación

| Archivo | Estado | Fase |
|---------|--------|------|
| `ocr/pytesseract_adapter.py` | ✅ Completo | Fase 2 |
| `ocr/gemini_vision_adapter.py` | ✅ Completo | Fase 2 |
| `ai/gemini_llm_provider.py` | ✅ Completo | Fase 2 — prompt engineering real |
| `ai/gemini_cache_proxy.py` | ✅ Completo | Proxy Pattern funcional |
| `persistence/database_session.py` | ✅ Completo | Engine + session lifecycle |
| `persistence/models.py` | ✅ Completo | 3 tablas ORM |
| `persistence/sqlalchemy_food_repository.py` | ✅ Completo | CRUD + mappers |
| `persistence/sqlalchemy_receipt_repository.py` | ✅ Completo | CRUD + mappers |
| `persistence/sqlalchemy_recipe_repository.py` | ✅ Completo | CRUD + mappers |

## Protocolo de Modificación

> Al implementar un adapter stub:
> 1. Reemplaza el `raise NotImplementedError(...)` con lógica real.
> 2. Asegúrate de que cumple con el contrato de la interfaz en Domain.
> 3. Agrega tests de integración en `tests/integration/`.
> 4. Actualiza ESTE README marcando el archivo como ✅ Completo.
> 5. Commit con: `feat(infrastructure): implement <adapter_name>`
