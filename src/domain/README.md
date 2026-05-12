# 🧠 Domain Layer — Núcleo de Negocio

> **Regla Fundamental:** Esta capa NO depende de NADA externo. Cero imports de frameworks,
> bases de datos, APIs, o librerías de terceros.

## Responsabilidades

1. **Entities** — Objetos de negocio con identidad única (Receipt, FoodItem, Recipe).
2. **Value Objects** — Objetos inmutables sin identidad (ExpirationDate, NutritionalInfo).
3. **Exceptions** — Jerarquía de errores de dominio.
4. **Interfaces (Ports)** — Contratos abstractos que la capa Infrastructure implementa.

## Patrones de Diseño en Esta Capa

| Patrón | Archivo | Descripción |
|--------|---------|-------------|
| **State Pattern** | `entities/receipt.py` | 5 estados concretos (`Uploaded`, `Processing`, `Parsed`, `Failed`, `Completed`) con transiciones validadas |
| **Strategy Pattern (Port)** | `interfaces/ocr_provider_interface.py` | Define el contrato que las estrategias OCR implementan |

## Estructura de Archivos

```
domain/
├── __init__.py
├── entities/
│   ├── __init__.py
│   ├── receipt.py          ← State Pattern (Aggregate Root)
│   ├── food_item.py        ← Entity con __lt__ para Heap ordering
│   └── recipe.py           ← Entity con relevance_score
├── value_objects/
│   ├── __init__.py
│   ├── expiration_date.py  ← Inmutable, factory method from_shelf_life()
│   └── nutritional_info.py ← Inmutable, datos nutricionales
├── exceptions/
│   ├── __init__.py
│   └── domain_exceptions.py ← 5 tipos de excepciones
└── interfaces/
    ├── __init__.py
    ├── ocr_provider_interface.py   ← Port para OCR (Strategy)
    ├── llm_provider_interface.py   ← Port para LLM (Proxy-wrapped)
    └── repository_interfaces.py    ← 3 repository ports
```

## Estructuras de Datos Integradas

- **List[str]** en `receipt.py` → `raw_text_lines` almacena texto OCR antes del parsing.
- **FoodItem.__lt__** habilita el uso en `ExpirationHeap` (Min-Heap).

## Estado de Implementación

| Archivo | Estado |
|---------|--------|
| `entities/receipt.py` | ✅ Completo — State Pattern funcional |
| `entities/food_item.py` | ✅ Completo — Domain logic + heap ordering |
| `entities/recipe.py` | ✅ Completo — Relevance scoring |
| `value_objects/*.py` | ✅ Completo |
| `exceptions/*.py` | ✅ Completo |
| `interfaces/*.py` | ✅ Completo — Todos los contratos definidos |

## Protocolo de Modificación

> ⚠️ **DIRECTIVA:** Esta capa es ESTABLE. No debe modificarse a menos que cambien
> las reglas de negocio fundamentales. Si necesitas agregar funcionalidad, extiende
> — no modifiques — las entidades existentes.
