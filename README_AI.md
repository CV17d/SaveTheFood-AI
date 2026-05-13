# 🤖 README_AI.md — Optimized Context for Language Models

> **DIRECTIVE:** This file is designed to be processed by LLMs (GPT, Gemini, Claude, etc.).
> If you are a language model reading this file, this is your entry point to understand
> the complete architecture of the **SaveTheFood AI** project. Read this ENTIRE document before
> generating any code.

---

## 1. Technical Executive Summary

**SaveTheFood AI** is an intelligent food-waste mitigation system built with
**Clean Architecture** in Python 3.11+.

### High-Level Pipeline

```text
Receipt (image) → OCR → Parsing → Expiration Estimation → RAG (Gemini) → Recipes → Dashboard
```

### Purpose

The system ingests supermarket receipts through OCR, extracts food products,
estimates their expiration dates using a **shelf-life hashmap** (O(1)), prioritizes the
most urgent ingredients through a **Min-Heap** (O(log N)), and generates contextualized
recipes using a **RAG Engine** (Gemini API) that maximizes the use of ingredients close
to expiration through a **Bipartite Graph**.

### Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| Architecture | Clean Architecture (4 layers) |
| OCR | PyTesseract + OpenCV / Gemini Vision |
| AI / RAG | Google Gemini API |
| Database | SQLite + SQLAlchemy ORM |
| Dashboard | Streamlit + Plotly |
| Testing | Pytest (unit, integration, e2e) |
| Code Quality | Ruff, MyPy (strict), Black |
| Containerization | Docker + Docker Compose |

---

## 2. Dependency Map — Clean Architecture

### Dependency Rule (INVIOLABLE)

```text
Source-code dependencies can ONLY point INWARD.
Nothing in an inner circle can know ANYTHING about an outer circle.
```

### Layer Diagram

```text
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION (Outer Layer)                    │
│  Streamlit UI, Pages, Components, ViewModels                     │
│  Depends on: Application (Use Cases, DTOs)                       │
│  NEVER imports: Domain entities directly                         │
├─────────────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE (Outer Layer)                  │
│  PyTesseract, Gemini API, SQLAlchemy, ORM Models                 │
│  IMPLEMENTS: Interfaces defined in Domain                        │
│  Depends on: Domain (interfaces), Shared (utils)                 │
│  NEVER imports: Application, Presentation                        │
├─────────────────────────────────────────────────────────────────┤
│                    APPLICATION (Middle Layer)                    │
│  Use Cases, DTOs, Application Services                           │
│  Orchestrates: Domain entities + Interfaces (Ports)              │
│  Depends on: Domain ONLY                                         │
│  NEVER imports: Infrastructure, Presentation                     │
├─────────────────────────────────────────────────────────────────┤
│                    DOMAIN (Core — Inner Layer)                   │
│  Entities, Value Objects, Exceptions, Interfaces/Protocols       │
│  Does NOT depend on anything external. Zero framework imports.   │
│  Defines: Contracts (Ports) that Infrastructure implements       │
└─────────────────────────────────────────────────────────────────┘
```

### Dependency Injection Flow

```text
DependencyContainer (src/shared/dependency_container.py)
    │
    ├── OCRProviderInterface ──→ PyTesseractAdapter | GeminiVisionAdapter
    │                            (Strategy Pattern — selected through env var)
    │
    ├── LLMProviderInterface ──→ GeminiCacheProxy(GeminiLLMProvider)
    │                            (Proxy Pattern — O(1) cache over API)
    │
    └── FoodItemRepositoryInterface ──→ SQLAlchemyFoodRepository
                                        (Repository Pattern — SQLite)
```

**Critical point:** The `DependencyContainer` is the ONLY file that imports concrete classes
from Infrastructure. Every other file programs against interfaces.

---

## 3. Data Flow Graph

### Complete Pipeline: Receipt → Recipe

```text
INPUT                           PROCESSING                          OUTPUT
─────                           ──────────                          ──────

┌──────────┐    ┌─────────────────────────────────────────────────────────────┐
│ Image    │    │                    INTERNAL PIPELINE                         │
│ Receipt  │───▶│                                                             │
│ (.jpg)   │    │  1. ProcessingQueue (FIFO)                                  │
│ └──────────┘    │     └─ Enqueues image for ordered processing                │
│                 │                                                             │
│                 │  2. Receipt Entity — State Pattern                          │
│                 │     └─ UPLOADED → PROCESSING → PARSED → COMPLETED          │
│                 │                                                             │
│                 │  3. OCR Strategy (PyTesseract | Gemini Vision)              │
│                 │     └─ Extracts List[str] of raw text lines                 │
│                 │                                                             │
│                 │  4. Parser → FoodItem Entities                              │
│                 │     └─ Normalizes names, extracts quantities                │
│                 │                                                             │
│                 │  5. ShelfLifeMap (Hashmap O(1))                             │
│                 │     └─ Estimates expiration date by product                 │
│                 │     └─ Fallback: LLM estimation if not found in the map     │
│                 │                                                             │
│                 │  6. ExpirationHeap (Min-Heap O(log N))                      │
│                 │     └─ Inserts FoodItems ordered by urgency                 │
│                 │                                                             │
│                 │  7. FoodCategoryTree (N-ary Tree)                           │
│                 │     └─ Classifies: Dairy → Cheese → Cheddar                │
│                 │                                                             │
│                 │  8. SQLAlchemy Repository                                   │
│                 │     └─ Persists entities in SQLite                          │
│                 │                                                             │
│                 │  9. RecipeGraph (Bipartite Graph)                           │
│                 │     └─ Connects expired/expiring ingredients with recipes   │
│                 │     └─ find_best_recipe() maximizes coverage               │
│                 │                                                             │
│                 │  10. GeminiCacheProxy → GeminiLLMProvider                   │
│                 │      └─ Generates RAG recipe with prioritized ingredients  │
│                 │      └─ O(1) cache avoids redundant API calls              │
│                 │                                                             │
│                 │  11. RecipeFactory (Factory Pattern)                        │
│                 │      └─ Builds Recipe entity from raw LLM response         │
│                 │                                                             │
│                 │  12. UndoStack (LIFO)                                       │
│                 │      └─ Allows rollback of manual OCR corrections          │
│                 └─────────────────────────────────────────────────────────────┘
│                                         │
│                                         ▼
│                 ┌─────────────────────────────────────────────────────────────┐
│                 │                    STREAMLIT DASHBOARD                       │
│                 │  ┌─────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│                 │  │  Inventory  │ │   Recipes    │ │   Impact Metrics    │ │
│                 │  │ (Heap View) │ │  (AI Gen)    │ │  (USD/CO₂ saved)    │ │
│                 │  └─────────────┘ └──────────────┘ └──────────────────────┘ │
│                 └─────────────────────────────────────────────────────────────┘
```

---

## 4. Interface Contracts — Required Abstract Methods

### ⚠️ CRITICAL: These methods MUST be implemented for the system to work.

### 4.1 OCRProviderInterface

**File:** `src/domain/interfaces/ocr_provider_interface.py`  
**Implementations:** `PyTesseractAdapter`, `GeminiVisionAdapter`

| Method | Signature | Description |
|---|---|---|
| `extract_text` | `(image_path: Path) → list[str]` | Extracts raw text lines from the receipt |
| `get_provider_name` | `() → str` | Returns the provider name for logging |

### 4.2 LLMProviderInterface

**File:** `src/domain/interfaces/llm_provider_interface.py`  
**Implementations:** `GeminiLLMProvider`, `GeminiCacheProxy`

| Method | Signature | Description |
|---|---|---|
| `generate_recipe` | `(ingredients: list[str], constraints: dict \| None) → dict` | Generates a recipe from ingredients |
| `estimate_shelf_life` | `(item_name: str) → int` | Estimates shelf life in days through the LLM |
| `get_provider_name` | `() → str` | Provider name for logging |

### 4.3 Repository Interfaces

**File:** `src/domain/interfaces/repository_interfaces.py`

#### ReceiptRepositoryInterface

| Method | Signature |
|---|---|
| `save` | `(receipt: Receipt) → None` |
| `find_by_id` | `(receipt_id: str) → Receipt \| None` |
| `find_all` | `() → list[Receipt]` |
| `delete` | `(receipt_id: str) → None` |

#### FoodItemRepositoryInterface

| Method | Signature |
|---|---|
| `save` | `(item: FoodItem) → None` |
| `save_batch` | `(items: list[FoodItem]) → None` |
| `find_by_id` | `(item_id: str) → FoodItem \| None` |
| `find_all` | `() → list[FoodItem]` |
| `find_expiring_within` | `(days: int) → list[FoodItem]` |
| `delete` | `(item_id: str) → None` |

#### RecipeRepositoryInterface

| Method | Signature |
|---|---|
| `save` | `(recipe: Recipe) → None` |
| `find_by_id` | `(recipe_id: str) → Recipe \| None` |
| `find_all` | `() → list[Recipe]` |
| `find_by_ingredient` | `(ingredient: str) → list[Recipe]` |

---

## 5. Design Patterns — Exact Location

| Pattern | File(s) | Purpose |
|---|---|---|
| **Strategy** | `ocr_provider_interface.py` → `pytesseract_adapter.py`, `gemini_vision_adapter.py` | Replaceable OCR without modifying use cases |
| **Factory** | `generate_recipe_usecase.py` → `RecipeFactory` | Builds Recipe entities from raw LLM output |
| **Proxy** | `gemini_cache_proxy.py` wraps `gemini_llm_provider.py` | O(1) cache over API calls to reduce latency/quota usage |
| **State** | `receipt.py` → `BaseReceiptState` + 5 concrete states | Receipt lifecycle with validated transitions |

---

## 6. Data Structures — Location and Justification

| # | Structure | File | Complexity | Use in the System |
|---|---|---|---|---|
| 1 | **List** | `receipt.py` → `raw_text_lines: list[str]` | O(1) append | Stores raw OCR text before parsing |
| 2 | **Stack (LIFO)** | `shared/data_structures/undo_stack.py` | O(1) push/pop | Rollback of manual OCR corrections |
| 3 | **Queue (FIFO)** | `shared/data_structures/processing_queue.py` | O(1) enqueue/dequeue | Image-processing pipeline |
| 4 | **Hashmap** | `shared/data_structures/shelf_life_map.py` | O(1) lookup | Instant shelf-life lookup by food item |
| 5 | **Heap (PQ)** | `shared/data_structures/expiration_heap.py` | O(log N) extract | Ingredient prioritization by expiration |
| 6 | **N-ary Tree** | `shared/data_structures/food_category_tree.py` | O(D) insert/search | Hierarchical food taxonomy |
| 7 | **Bipartite Graph** | `shared/data_structures/recipe_graph.py` | O(1) add_edge | Recipe recommendation based on ingredient coverage |

---

## 7. Current Context Status — Implementation Map

### ✅ Implemented (Functional Logic)

| File | Status | Description |
|---|---|---|
| `domain/entities/receipt.py` | ✅ COMPLETE | State Pattern with 5 states + transitions |
| `domain/entities/food_item.py` | ✅ COMPLETE | Entity with urgency_level, __lt__ for heap |
| `domain/entities/recipe.py` | ✅ COMPLETE | Entity with relevance_score |
| `domain/value_objects/expiration_date.py` | ✅ COMPLETE | Immutable Value Object |
| `domain/value_objects/nutritional_info.py` | ✅ COMPLETE | Immutable Value Object |
| `domain/exceptions/domain_exceptions.py` | ✅ COMPLETE | Exception hierarchy |
| `domain/interfaces/*.py` | ✅ COMPLETE | All contracts/ports defined |
| `shared/data_structures/undo_stack.py` | ✅ COMPLETE | Generic stack with max_size |
| `shared/data_structures/processing_queue.py` | ✅ COMPLETE | Queue with backpressure |
| `shared/data_structures/expiration_heap.py` | ✅ COMPLETE | Min-heap with heapq |
| `shared/data_structures/food_category_tree.py` | ✅ COMPLETE | N-ary tree with DFS + to_dict |
| `shared/data_structures/recipe_graph.py` | ✅ COMPLETE | Bipartite graph with ranking |
| `shared/data_structures/shelf_life_map.py` | ✅ COMPLETE | Hashmap with 40+ entries |
| `shared/dependency_container.py` | ✅ COMPLETE | DI container with Strategy + Proxy wiring |
| `infrastructure/ai/gemini_llm_provider.py` | ✅ COMPLETE | Prompt engineering + JSON parsing |
| `infrastructure/ai/gemini_cache_proxy.py` | ✅ COMPLETE | Proxy Pattern with TTL + eviction |
| `infrastructure/persistence/database_session.py` | ✅ COMPLETE | SQLAlchemy engine/session |
| `infrastructure/persistence/models.py` | ✅ COMPLETE | ORM models for 3 tables |
| `infrastructure/persistence/sqlalchemy_food_repository.py` | ✅ COMPLETE | Repository with entity↔model mappers |
| `application/use_cases/process_receipt_usecase.py` | ✅ COMPLETE | Pipeline + Queue/Map/Tree integration |
| `application/use_cases/generate_recipe_usecase.py` | ✅ COMPLETE | RAG + Heap/Graph integration |
| `application/services/dashboard_metrics_service.py` | ✅ COMPLETE | Economic/environmental metrics |
| `application/dtos/*.py` | ✅ COMPLETE | Frozen DTOs for UI |
| `tests/unit/test_food_item.py` | ✅ COMPLETE | Tests for 7 data structures + entity |
| `tests/unit/test_process_receipt.py` | ✅ COMPLETE | Tests for State Pattern lifecycle |
| `config/settings.py` | ✅ COMPLETE | Pydantic Settings |

### 🔧 Stub / Boilerplate (Requires Implementation)

| File | Phase | Missing Work |
|---|---|---|
| `infrastructure/ocr/pytesseract_adapter.py` | Phase 2 | OpenCV + PyTesseract logic |
| `infrastructure/ocr/gemini_vision_adapter.py` | Phase 2 | Multimodal call to Gemini API |
| `presentation/app.py` | Phase 3 | Streamlit multipage setup |
| `presentation/components/sidebar.py` | Phase 3 | Navigation + upload widget |
| `presentation/components/charts.py` | Phase 3 | Plotly sunburst/treemap/gauges |
| `presentation/pages/inventory.py` | Phase 3 | Heap view + undo stack UI |
| `presentation/pages/recipes.py` | Phase 3 | Recipe cards + graph visualization |
| `presentation/view_models/inventory_viewmodel.py` | Phase 3 | Domain→UI transformation |
| `tests/integration/test_ocr_pipeline.py` | Phase 2 | Tests with real images |
| `tests/e2e/test_full_pipeline.py` | Phase 3 | Complete end-to-end tests |

---

## 8. Complete Directory Tree

```text
SaveTheFood-AI/
├── pyproject.toml                          # Dependencies, Ruff, MyPy, Pytest
├── Makefile                                # make install/test/lint/run
├── Dockerfile                              # Multi-stage build
├── docker-compose.yml                      # App + DB init services
├── .env.example                            # Environment variable template
├── .pre-commit-config.yaml                 # Quality hooks
├── .gitignore
├── README.md                               # Public project README
├── README_AI.md                            # ← THIS FILE (context for LLMs)
│
├── src/                                    # Main source code
│   ├── domain/                             # INNER layer — no dependencies
│   │   ├── entities/
│   │   │   ├── receipt.py                  # State Pattern (5 states)
│   │   │   ├── food_item.py                # Entity with __lt__ for heap
│   │   │   └── recipe.py                   # Entity with relevance_score
│   │   ├── value_objects/
│   │   │   ├── expiration_date.py          # Immutable VO
│   │   │   └── nutritional_info.py         # Immutable VO
│   │   ├── exceptions/
│   │   │   └── domain_exceptions.py        # Exception hierarchy
│   │   └── interfaces/                     # PORTS (contracts)
│   │       ├── ocr_provider_interface.py   # Strategy Pattern port
│   │       ├── llm_provider_interface.py   # LLM port (Proxy-wrapped)
│   │       └── repository_interfaces.py    # 3 repository ports
│   │
│   ├── application/                        # MIDDLE layer — orchestration
│   │   ├── use_cases/
│   │   │   ├── process_receipt_usecase.py  # Complete OCR pipeline
│   │   │   └── generate_recipe_usecase.py  # RAG + RecipeFactory
│   │   ├── services/
│   │   │   └── dashboard_metrics_service.py # USD/CO₂ metrics
│   │   └── dtos/
│   │       ├── receipt_dto.py              # DTOs for Receipt/FoodItem
│   │       └── recipe_dto.py               # DTO for Recipe
│   │
│   ├── infrastructure/                     # OUTER layer — implementations
│   │   ├── ocr/
│   │   │   ├── pytesseract_adapter.py      # Strategy: local OCR
│   │   │   └── gemini_vision_adapter.py    # Strategy: cloud OCR
│   │   ├── ai/
│   │   │   ├── gemini_llm_provider.py      # Concrete LLM
│   │   │   └── gemini_cache_proxy.py       # Proxy Pattern (cache)
│   │   └── persistence/
│   │       ├── database_session.py         # SQLAlchemy engine
│   │       ├── models.py                   # ORM models (3 tables)
│   │       └── sqlalchemy_food_repository.py # Concrete repository
│   │
│   ├── presentation/                       # OUTER layer — UI
│   │   ├── app.py                          # Streamlit entrypoint
│   │   ├── components/
│   │   │   ├── sidebar.py                  # Navigation
│   │   │   └── charts.py                   # Plotly visualizations
│   │   ├── pages/
│   │   │   ├── inventory.py                # Heap view + Undo Stack
│   │   │   └── recipes.py                  # AI recipes + Graph viz
│   │   └── view_models/
│   │       └── inventory_viewmodel.py      # Domain → UI transform
│   │
│   └── shared/                             # Cross-cutting concerns
│       ├── constants.py                    # Global constants
│       ├── logger.py                       # Structured logging
│       ├── utils.py                        # Shared utilities
│       ├── dependency_container.py         # Composition Root (DI)
│       └── data_structures/                # 6 implemented DSs
│           ├── undo_stack.py               # LIFO Stack
│           ├── processing_queue.py         # FIFO Queue
│           ├── expiration_heap.py          # Min-Heap (PQ)
│           ├── food_category_tree.py       # N-ary Tree
│           ├── recipe_graph.py             # Bipartite Graph
│           └── shelf_life_map.py           # O(1) Hashmap
│
├── tests/
│   ├── conftest.py                         # Shared fixtures
│   ├── unit/
│   │   ├── test_food_item.py               # Tests: 7 DSs + entities
│   │   └── test_process_receipt.py         # Tests: State Pattern
│   ├── integration/
│   │   └── test_ocr_pipeline.py            # Tests: OCR (stub)
│   └── e2e/
│       └── test_full_pipeline.py           # Tests: complete pipeline (stub)
│
├── config/
│   └── settings.py                         # Pydantic Settings
│ ├── scripts/
│   ├── migrate_db.py                       # Create SQLite tables
│   └── seed_shelf_life.py                  # Seed the hashmap
│ ├── data/
│   ├── raw/                                # Receipt images
│   ├── processed/                          # Parsed data
│   └── db/                                 # SQLite DB files
│ ├── assets/                               # Static files
│ ├── notebooks/                            # Jupyter experimentation
│ └── docs/
│     └── api_specs.md                      # API specifications
```

---

## 9. Instructions for LLMs — How to Continue Development

### If you must implement Phase 2:

1. Read `src/domain/interfaces/` — these are the contracts you must satisfy.
2. Implement `pytesseract_adapter.py` using OpenCV for preprocessing.
3. Implement `gemini_llm_provider.py` with structured prompt engineering.
4. Write integration tests in `tests/integration/test_ocr_pipeline.py`.
5. **DO NOT modify** any file in `src/domain/` — it is immutable.

### If you must implement Phase 3:

1. Read `src/application/dtos/` — these are the data structures the UI must render.
2. Implement `app.py` with Streamlit multipage.
3. Use `ExpirationHeap` for the sorted inventory view.
4. Use `UndoStack` for the undo feature for OCR corrections.
5. Integrate Plotly charts using data from `DashboardMetricsService`.

### Golden Rule

```text
NEVER import concrete Infrastructure classes in Application or Domain.
ALWAYS program against the interfaces defined in src/domain/interfaces/.
The ONLY place where concrete implementations are wired is dependency_container.py.
```
