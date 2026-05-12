# 🤖 README_AI.md — Contexto Optimizado para Modelos de Lenguaje

> **DIRECTIVA:** Este archivo está diseñado para ser procesado por LLMs (GPT, Gemini, Claude, etc.).
> Si eres un modelo de lenguaje leyendo este archivo, este es tu punto de entrada para comprender
> la arquitectura completa del proyecto **SaveTheFood AI**. Lee este documento COMPLETO antes de
> generar cualquier código.

---

## 1. Resumen Ejecutivo Técnico

**SaveTheFood AI** es un sistema inteligente de mitigación de desperdicio alimentario construido
con **Clean Architecture** en Python 3.11+.

### Pipeline de Alto Nivel

```
Recibo (imagen) → OCR → Parsing → Estimación de Vencimiento → RAG (Gemini) → Recetas → Dashboard
```

### Propósito

El sistema ingiere recibos de supermercado mediante OCR, extrae los productos alimenticios,
estima sus fechas de vencimiento usando un **Hashmap de vida útil** (O(1)), prioriza los
ingredientes más urgentes mediante un **Min-Heap** (O(log N)), y genera recetas contextualizadas
usando un **Motor RAG** (Gemini API) que maximiza el uso de ingredientes próximos a vencer
a través de un **Grafo Bipartito**.

### Stack Tecnológico

| Componente         | Tecnología                          |
|--------------------|-------------------------------------|
| Lenguaje           | Python 3.11+                        |
| Arquitectura       | Clean Architecture (4 capas)        |
| OCR                | PyTesseract + OpenCV / Gemini Vision|
| IA / RAG           | Google Gemini API                   |
| Base de Datos      | SQLite + SQLAlchemy ORM             |
| Dashboard          | Streamlit + Plotly                   |
| Testing            | Pytest (unit, integration, e2e)     |
| Calidad de Código  | Ruff, MyPy (strict), Black          |
| Contenedorización  | Docker + Docker Compose             |

---

## 2. Mapa de Dependencias — Clean Architecture

### Regla de Dependencia (INVIOLABLE)

```
Las dependencias del código fuente SOLO pueden apuntar HACIA ADENTRO.
Nada en un círculo interno puede saber NADA sobre un círculo externo.
```

### Diagrama de Capas

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION (Capa Externa)                   │
│  Streamlit UI, Pages, Components, ViewModels                     │
│  Depende de: Application (Use Cases, DTOs)                       │
│  NUNCA importa: Domain entities directamente                     │
├─────────────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE (Capa Externa)                 │
│  PyTesseract, Gemini API, SQLAlchemy, ORM Models                │
│  IMPLEMENTA: Interfaces definidas en Domain                      │
│  Depende de: Domain (interfaces), Shared (utils)                │
│  NUNCA importa: Application, Presentation                        │
├─────────────────────────────────────────────────────────────────┤
│                    APPLICATION (Capa Intermedia)                 │
│  Use Cases, DTOs, Application Services                           │
│  Orquesta: Entidades de Domain + Interfaces (Ports)             │
│  Depende de: Domain SOLAMENTE                                    │
│  NUNCA importa: Infrastructure, Presentation                     │
├─────────────────────────────────────────────────────────────────┤
│                    DOMAIN (Núcleo — Capa Interna)                │
│  Entities, Value Objects, Exceptions, Interfaces/Protocols      │
│  NO depende de NADA externo. Cero imports de frameworks.        │
│  Define: Contratos (Ports) que Infrastructure implementa        │
└─────────────────────────────────────────────────────────────────┘
```

### Flujo de Inyección de Dependencias

```
DependencyContainer (src/shared/dependency_container.py)
    │
    ├── OCRProviderInterface ──→ PyTesseractAdapter | GeminiVisionAdapter
    │                            (Strategy Pattern — selección por env var)
    │
    ├── LLMProviderInterface ──→ GeminiCacheProxy(GeminiLLMProvider)
    │                            (Proxy Pattern — cache O(1) sobre API)
    │
    └── FoodItemRepositoryInterface ──→ SQLAlchemyFoodRepository
                                        (Repository Pattern — SQLite)
```

**Punto crítico:** El `DependencyContainer` es el ÚNICO archivo que importa clases concretas
de Infrastructure. Todos los demás archivos programan contra interfaces.

---

## 3. Grafo de Flujo de Datos

### Pipeline Completo: Recibo → Receta

```
INPUT                           PROCESSING                          OUTPUT
─────                           ──────────                          ──────

┌──────────┐    ┌─────────────────────────────────────────────────────────────┐
│ Imagen   │    │                    PIPELINE INTERNO                         │
│ Recibo   │───▶│                                                             │
│ (.jpg)   │    │  1. ProcessingQueue (FIFO)                                  │
└──────────┘    │     └─ Encola imagen para procesamiento ordenado            │
                │                                                             │
                │  2. Receipt Entity — State Pattern                          │
                │     └─ UPLOADED → PROCESSING → PARSED → COMPLETED          │
                │                                                             │
                │  3. OCR Strategy (PyTesseract | Gemini Vision)              │
                │     └─ Extrae List[str] de líneas de texto raw              │
                │                                                             │
                │  4. Parser → FoodItem Entities                              │
                │     └─ Normaliza nombres, extrae cantidades                 │
                │                                                             │
                │  5. ShelfLifeMap (Hashmap O(1))                             │
                │     └─ Estima fecha de vencimiento por producto             │
                │     └─ Fallback: LLM estimation si no existe en el mapa    │
                │                                                             │
                │  6. ExpirationHeap (Min-Heap O(log N))                      │
                │     └─ Inserta FoodItems ordenados por urgencia             │
                │                                                             │
                │  7. FoodCategoryTree (Árbol N-ario)                         │
                │     └─ Clasifica: Dairy → Cheese → Cheddar                 │
                │                                                             │
                │  8. SQLAlchemy Repository                                   │
                │     └─ Persiste entidades en SQLite                         │
                │                                                             │
                │  9. RecipeGraph (Grafo Bipartito)                           │
                │     └─ Conecta ingredientes vencidos con recetas            │
                │     └─ find_best_recipe() maximiza cobertura               │
                │                                                             │
                │  10. GeminiCacheProxy → GeminiLLMProvider                   │
                │      └─ Genera receta RAG con ingredientes priorizados     │
                │      └─ Cache O(1) evita llamadas redundantes a API        │
                │                                                             │
                │  11. RecipeFactory (Factory Pattern)                         │
                │      └─ Construye Recipe entity desde respuesta LLM        │
                │                                                             │  
                │  12. UndoStack (LIFO)                                       │
                │      └─ Permite deshacer correcciones manuales de OCR      │
                └─────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
                ┌─────────────────────────────────────────────────────────────┐
                │                    STREAMLIT DASHBOARD                       │
                │  ┌─────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
                │  │  Inventario  │ │   Recetas    │ │  Métricas Impacto   │ │
                │  │  (Heap View) │ │  (AI Gen)    │ │  (USD/CO₂ ahorrado) │ │
                │  └─────────────┘ └──────────────┘ └──────────────────────┘ │
                └─────────────────────────────────────────────────────────────┘
```

---

## 4. Contrato de Interfaces — Métodos Abstractos Obligatorios

### ⚠️ CRÍTICO: Estos métodos DEBEN ser implementados para que el sistema funcione.

### 4.1 OCRProviderInterface

**Archivo:** `src/domain/interfaces/ocr_provider_interface.py`
**Implementaciones:** `PyTesseractAdapter`, `GeminiVisionAdapter`

| Método | Signature | Descripción |
|--------|-----------|-------------|
| `extract_text` | `(image_path: Path) → list[str]` | Extrae líneas de texto raw del recibo |
| `get_provider_name` | `() → str` | Retorna nombre del proveedor para logging |

### 4.2 LLMProviderInterface

**Archivo:** `src/domain/interfaces/llm_provider_interface.py`
**Implementaciones:** `GeminiLLMProvider`, `GeminiCacheProxy`

| Método | Signature | Descripción |
|--------|-----------|-------------|
| `generate_recipe` | `(ingredients: list[str], constraints: dict \| None) → dict` | Genera receta desde ingredientes |
| `estimate_shelf_life` | `(item_name: str) → int` | Estima vida útil en días vía LLM |
| `get_provider_name` | `() → str` | Nombre del proveedor para logging |

### 4.3 Repository Interfaces

**Archivo:** `src/domain/interfaces/repository_interfaces.py`

#### ReceiptRepositoryInterface

| Método | Signature |
|--------|-----------|
| `save` | `(receipt: Receipt) → None` |
| `find_by_id` | `(receipt_id: str) → Receipt \| None` |
| `find_all` | `() → list[Receipt]` |
| `delete` | `(receipt_id: str) → None` |

#### FoodItemRepositoryInterface

| Método | Signature |
|--------|-----------|
| `save` | `(item: FoodItem) → None` |
| `save_batch` | `(items: list[FoodItem]) → None` |
| `find_by_id` | `(item_id: str) → FoodItem \| None` |
| `find_all` | `() → list[FoodItem]` |
| `find_expiring_within` | `(days: int) → list[FoodItem]` |
| `delete` | `(item_id: str) → None` |

#### RecipeRepositoryInterface

| Método | Signature |
|--------|-----------|
| `save` | `(recipe: Recipe) → None` |
| `find_by_id` | `(recipe_id: str) → Recipe \| None` |
| `find_all` | `() → list[Recipe]` |
| `find_by_ingredient` | `(ingredient: str) → list[Recipe]` |

---

## 5. Patrones de Diseño — Ubicación Exacta

| Patrón | Archivo(s) | Propósito |
|--------|------------|-----------|
| **Strategy** | `ocr_provider_interface.py` → `pytesseract_adapter.py`, `gemini_vision_adapter.py` | OCR intercambiable sin modificar use cases |
| **Factory** | `generate_recipe_usecase.py` → `RecipeFactory` | Construcción de entidades Recipe desde raw LLM output |
| **Proxy** | `gemini_cache_proxy.py` wraps `gemini_llm_provider.py` | Cache O(1) sobre llamadas API para reducir latencia/quota |
| **State** | `receipt.py` → `BaseReceiptState` + 5 estados concretos | Lifecycle del recibo con transiciones validadas |

---

## 6. Estructuras de Datos — Ubicación y Justificación

| # | Estructura | Archivo | Complejidad | Uso en el Sistema |
|---|------------|---------|-------------|-------------------|
| 1 | **List** | `receipt.py` → `raw_text_lines: list[str]` | O(1) append | Almacena texto OCR raw antes del parsing |
| 2 | **Stack (LIFO)** | `shared/data_structures/undo_stack.py` | O(1) push/pop | Rollback de correcciones manuales de OCR |
| 3 | **Queue (FIFO)** | `shared/data_structures/processing_queue.py` | O(1) enqueue/dequeue | Pipeline de procesamiento de imágenes |
| 4 | **Hashmap** | `shared/data_structures/shelf_life_map.py` | O(1) lookup | Consulta instantánea de vida útil por alimento |
| 5 | **Heap (PQ)** | `shared/data_structures/expiration_heap.py` | O(log N) extract | Priorización de ingredientes por vencimiento |
| 6 | **Árbol N-ario** | `shared/data_structures/food_category_tree.py` | O(D) insert/search | Taxonomía jerárquica de alimentos |
| 7 | **Grafo Bipartito** | `shared/data_structures/recipe_graph.py` | O(1) add_edge | Recomendación de recetas por cobertura de ingredientes |

---

## 7. Estado Actual del Contexto — Mapa de Implementación

### ✅ Implementado (Lógica Funcional)

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `domain/entities/receipt.py` | ✅ COMPLETO | State Pattern con 5 estados + transiciones |
| `domain/entities/food_item.py` | ✅ COMPLETO | Entity con urgency_level, __lt__ para heap |
| `domain/entities/recipe.py` | ✅ COMPLETO | Entity con relevance_score |
| `domain/value_objects/expiration_date.py` | ✅ COMPLETO | Value Object inmutable |
| `domain/value_objects/nutritional_info.py` | ✅ COMPLETO | Value Object inmutable |
| `domain/exceptions/domain_exceptions.py` | ✅ COMPLETO | Jerarquía de excepciones |
| `domain/interfaces/*.py` | ✅ COMPLETO | Todos los contratos/ports definidos |
| `shared/data_structures/undo_stack.py` | ✅ COMPLETO | Stack genérico con max_size |
| `shared/data_structures/processing_queue.py` | ✅ COMPLETO | Queue con backpressure |
| `shared/data_structures/expiration_heap.py` | ✅ COMPLETO | Min-heap con heapq |
| `shared/data_structures/food_category_tree.py` | ✅ COMPLETO | N-ary tree con DFS + to_dict |
| `shared/data_structures/recipe_graph.py` | ✅ COMPLETO | Grafo bipartito con ranking |
| `shared/data_structures/shelf_life_map.py` | ✅ COMPLETO | Hashmap con 40+ entradas |
| `shared/dependency_container.py` | ✅ COMPLETO | DI container con Strategy + Proxy wiring |
| `infrastructure/ai/gemini_cache_proxy.py` | ✅ COMPLETO | Proxy Pattern con TTL + eviction |
| `infrastructure/persistence/database_session.py` | ✅ COMPLETO | SQLAlchemy engine/session |
| `infrastructure/persistence/models.py` | ✅ COMPLETO | ORM models para 3 tablas |
| `infrastructure/persistence/sqlalchemy_food_repository.py` | ✅ COMPLETO | Repository con mappers entity↔model |
| `application/use_cases/process_receipt_usecase.py` | ✅ COMPLETO | Pipeline orquestador |
| `application/use_cases/generate_recipe_usecase.py` | ✅ COMPLETO | RecipeFactory + LLM invocation |
| `application/services/dashboard_metrics_service.py` | ✅ COMPLETO | Métricas económicas/ambientales |
| `application/dtos/*.py` | ✅ COMPLETO | DTOs frozen para UI |
| `tests/unit/test_food_item.py` | ✅ COMPLETO | Tests para 7 data structures + entity |
| `tests/unit/test_process_receipt.py` | ✅ COMPLETO | Tests para State Pattern lifecycle |
| `config/settings.py` | ✅ COMPLETO | Pydantic Settings |

### 🔧 Stub / Boilerplate (Requiere Implementación)

| Archivo | Fase | Lo que Falta |
|---------|------|-------------|
| `infrastructure/ocr/pytesseract_adapter.py` | Fase 2 | Lógica OpenCV + PyTesseract |
| `infrastructure/ocr/gemini_vision_adapter.py` | Fase 2 | Llamada multimodal a Gemini API |
| `infrastructure/ai/gemini_llm_provider.py` | Fase 2 | Prompt engineering + parsing JSON |
| `presentation/app.py` | Fase 3 | Streamlit multipage setup |
| `presentation/components/sidebar.py` | Fase 3 | Navegación + upload widget |
| `presentation/components/charts.py` | Fase 3 | Plotly sunburst/treemap/gauges |
| `presentation/pages/inventory.py` | Fase 3 | Heap view + undo stack UI |
| `presentation/pages/recipes.py` | Fase 3 | Recipe cards + graph viz |
| `presentation/view_models/inventory_viewmodel.py` | Fase 3 | Transformación domain→UI |
| `tests/integration/test_ocr_pipeline.py` | Fase 2 | Tests con imágenes reales |
| `tests/e2e/test_full_pipeline.py` | Fase 3 | Tests end-to-end completos |

---

## 8. Árbol de Directorios Completo

```
SaveTheFood-AI/
├── pyproject.toml                          # Dependencias, Ruff, MyPy, Pytest
├── Makefile                                # make install/test/lint/run
├── Dockerfile                              # Multi-stage build
├── docker-compose.yml                      # App + DB init services
├── .env.example                            # Variables de entorno template
├── .pre-commit-config.yaml                 # Hooks de calidad
├── .gitignore
├── README.md                               # README público del proyecto
├── README_AI.md                            # ← ESTE ARCHIVO (contexto para LLMs)
│
├── src/                                    # Código fuente principal
│   ├── domain/                             # Capa INTERNA — sin dependencias
│   │   ├── entities/
│   │   │   ├── receipt.py                  # State Pattern (5 estados)
│   │   │   ├── food_item.py               # Entity con __lt__ para heap
│   │   │   └── recipe.py                  # Entity con relevance_score
│   │   ├── value_objects/
│   │   │   ├── expiration_date.py         # VO inmutable
│   │   │   └── nutritional_info.py        # VO inmutable
│   │   ├── exceptions/
│   │   │   └── domain_exceptions.py       # Jerarquía de excepciones
│   │   └── interfaces/                    # PORTS (contratos)
│   │       ├── ocr_provider_interface.py  # Strategy Pattern port
│   │       ├── llm_provider_interface.py  # LLM port (Proxy-wrapped)
│   │       └── repository_interfaces.py   # 3 repository ports
│   │
│   ├── application/                        # Capa INTERMEDIA — orquestación
│   │   ├── use_cases/
│   │   │   ├── process_receipt_usecase.py # Pipeline OCR completo
│   │   │   └── generate_recipe_usecase.py # RAG + RecipeFactory
│   │   ├── services/
│   │   │   └── dashboard_metrics_service.py # Métricas USD/CO₂
│   │   └── dtos/
│   │       ├── receipt_dto.py             # DTOs para Receipt/FoodItem
│   │       └── recipe_dto.py             # DTO para Recipe
│   │
│   ├── infrastructure/                     # Capa EXTERNA — implementaciones
│   │   ├── ocr/
│   │   │   ├── pytesseract_adapter.py     # Strategy: OCR local
│   │   │   └── gemini_vision_adapter.py   # Strategy: OCR cloud
│   │   ├── ai/
│   │   │   ├── gemini_llm_provider.py     # LLM concreto
│   │   │   └── gemini_cache_proxy.py      # Proxy Pattern (cache)
│   │   └── persistence/
│   │       ├── database_session.py        # SQLAlchemy engine
│   │       ├── models.py                  # ORM models (3 tablas)
│   │       └── sqlalchemy_food_repository.py # Repository concreto
│   │
│   ├── presentation/                       # Capa EXTERNA — UI
│   │   ├── app.py                         # Streamlit entrypoint
│   │   ├── components/
│   │   │   ├── sidebar.py                 # Navegación
│   │   │   └── charts.py                 # Plotly visualizaciones
│   │   ├── pages/
│   │   │   ├── inventory.py              # Heap view + Undo Stack
│   │   │   └── recipes.py               # Recetas AI + Graph viz
│   │   └── view_models/
│   │       └── inventory_viewmodel.py    # Domain → UI transform
│   │
│   └── shared/                             # Cross-cutting concerns
│       ├── constants.py                   # Constantes globales
│       ├── logger.py                      # Logging estructurado
│       ├── utils.py                       # Utilidades compartidas
│       ├── dependency_container.py        # Composition Root (DI)
│       └── data_structures/              # 6 EDs implementadas
│           ├── undo_stack.py             # Stack LIFO
│           ├── processing_queue.py       # Queue FIFO
│           ├── expiration_heap.py        # Min-Heap (PQ)
│           ├── food_category_tree.py     # Árbol N-ario
│           ├── recipe_graph.py           # Grafo Bipartito
│           └── shelf_life_map.py         # Hashmap O(1)
│
├── tests/
│   ├── conftest.py                        # Fixtures compartidos
│   ├── unit/
│   │   ├── test_food_item.py             # Tests: 7 EDs + entities
│   │   └── test_process_receipt.py       # Tests: State Pattern
│   ├── integration/
│   │   └── test_ocr_pipeline.py          # Tests: OCR (stub)
│   └── e2e/
│       └── test_full_pipeline.py         # Tests: pipeline completo (stub)
│
├── config/
│   └── settings.py                        # Pydantic Settings
├── scripts/
│   ├── migrate_db.py                      # Crear tablas SQLite
│   └── seed_shelf_life.py                # Seed del hashmap
├── data/
│   ├── raw/                               # Imágenes de recibos
│   ├── processed/                         # Datos parseados
│   └── db/                                # SQLite DB files
├── assets/                                # Archivos estáticos
├── notebooks/                             # Experimentación Jupyter
└── docs/
    └── api_specs.md                       # Especificaciones API
```

---

## 9. Instrucciones para LLMs — Cómo Continuar el Desarrollo

### Si debes implementar Fase 2:

1. Lee `src/domain/interfaces/` — estos son los contratos que debes cumplir.
2. Implementa `pytesseract_adapter.py` usando OpenCV para preprocessing.
3. Implementa `gemini_llm_provider.py` con prompt engineering estructurado.
4. Escribe tests de integración en `tests/integration/test_ocr_pipeline.py`.
5. **NO modifiques** ningún archivo en `src/domain/` — es inmutable.

### Si debes implementar Fase 3:

1. Lee `src/application/dtos/` — estos son los datos que la UI debe renderizar.
2. Implementa `app.py` con Streamlit multipage.
3. Usa `ExpirationHeap` para la vista de inventario ordenada.
4. Usa `UndoStack` para el feature de deshacer correcciones OCR.
5. Integra Plotly charts usando datos de `DashboardMetricsService`.

### Regla de Oro

```
NUNCA importes clases concretas de Infrastructure en Application o Domain.
SIEMPRE programa contra las interfaces definidas en src/domain/interfaces/.
El ÚNICO lugar donde se conectan implementaciones concretas es dependency_container.py.
```
