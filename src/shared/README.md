# 🛠️ Shared Layer — Concerns Transversales

> **Responsabilidad:** Proveer utilidades, constantes, logging, inyección de dependencias,
> y las implementaciones de las 6 estructuras de datos avanzadas que el sistema utiliza.

## Responsabilidades

1. **Constants** — Valores de configuración centralizados.
2. **Logger** — Logging estructurado con formato timestamp.
3. **Utils** — Funciones de utilidad compartidas entre capas.
4. **DependencyContainer** — Composition Root para inyección de dependencias.
5. **Data Structures** — 6 estructuras de datos avanzadas con documentación de complejidad.

## Estructura de Archivos

```
shared/
├── __init__.py
├── constants.py                        ← Constantes globales
├── logger.py                           ← Factory de loggers estructurados
├── utils.py                            ← normalize_food_name(), truncate()
├── dependency_container.py             ← Composition Root (Strategy + Proxy wiring)
└── data_structures/
    ├── __init__.py
    ├── undo_stack.py                   ← Stack LIFO — Undo de correcciones OCR
    ├── processing_queue.py             ← Queue FIFO — Pipeline de procesamiento
    ├── expiration_heap.py              ← Min-Heap — Prioridad por vencimiento
    ├── food_category_tree.py           ← Árbol N-ario — Taxonomía alimentaria
    ├── recipe_graph.py                 ← Grafo Bipartito — Recomendación recetas
    └── shelf_life_map.py               ← Hashmap — Vida útil O(1)
```

## Mapa de Estructuras de Datos

| # | ED | Clase | Complejidad | Dónde se Usa |
|---|-----|-------|-------------|--------------|
| 1 | **List** | Python built-in | O(1) append | `Receipt.raw_text_lines` — texto OCR raw |
| 2 | **Stack (LIFO)** | `UndoStack[T]` | O(1) push/pop | UI: deshacer correcciones manuales |
| 3 | **Queue (FIFO)** | `ProcessingQueue[T]` | O(1) enq/deq | Pipeline de procesamiento de recibos |
| 4 | **Hashmap** | `ShelfLifeMap` | O(1) get/set | Consulta de vida útil por alimento |
| 5 | **Heap (PQ)** | `ExpirationHeap[T]` | O(log N) extract | Priorización por vencimiento |
| 6 | **Árbol N-ario** | `FoodCategoryTree` | O(D) insert | Categorización jerárquica |
| 7 | **Grafo Bipartito** | `RecipeGraph` | O(1) add_edge | Motor de recomendación de recetas |

## Estado de Implementación

| Archivo | Estado |
|---------|--------|
| `constants.py` | ✅ Completo |
| `logger.py` | ✅ Completo |
| `utils.py` | ✅ Completo |
| `dependency_container.py` | ✅ Completo |
| `data_structures/*.py` (6 archivos) | ✅ Completo — Todos funcionales con docstrings |

## Protocolo de Modificación

> Al agregar una nueva estructura de datos:
> 1. Créala en `data_structures/` con docstring detallado (PURPOSE, WHERE, COMPLEXITY, WHY).
> 2. Expórtala desde `data_structures/__init__.py`.
> 3. Agrega tests unitarios en `tests/unit/`.
> 4. Actualiza la tabla de EDs en ESTE README y en `README_AI.md`.
