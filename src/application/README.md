# ⚙️ Application Layer — Orquestación de Casos de Uso

> **Responsabilidad:** Coordinar la ejecución de lógica de negocio utilizando
> entidades del Domain e interfaces (Ports). NUNCA importa clases concretas
> de Infrastructure.

## Responsabilidades

1. **Use Cases** — Orquestadores que coordinan el flujo de datos entre entidades e interfaces.
2. **DTOs** — Data Transfer Objects inmutables que desacoplan Domain de Presentation.
3. **Application Services** — Servicios de lectura/agregación (no mutan entidades).

## Patrones de Diseño en Esta Capa

| Patrón | Archivo | Descripción |
|--------|---------|-------------|
| **Factory Pattern** | `use_cases/generate_recipe_usecase.py` → `RecipeFactory` | Construye entidades Recipe desde output raw del LLM |

## Estructura de Archivos

```
application/
├── __init__.py
├── use_cases/
│   ├── __init__.py
│   ├── process_receipt_usecase.py  ← Pipeline completo: imagen → FoodItems
│   └── generate_recipe_usecase.py  ← RAG: ingredientes → Receta + Factory
├── services/
│   ├── __init__.py
│   └── dashboard_metrics_service.py ← Métricas económicas y ambientales
└── dtos/
    ├── __init__.py
    ├── receipt_dto.py              ← DTOs para Receipt y FoodItem
    └── recipe_dto.py              ← DTO para Recipe
```

## Flujo de Datos por Use Case

### ProcessReceiptUseCase

```
imagen.jpg → OCRProvider.extract_text() → List[str] raw
           → Parser → List[FoodItem]
           → ShelfLifeMap → expiration_date estimada
           → Repository.save_batch()
           → Receipt.state: UPLOADED → PROCESSING → PARSED → COMPLETED
```

### GenerateRecipeUseCase

```
FoodItemRepo.find_expiring_within(5) → List[FoodItem] urgentes
           → LLMProvider.generate_recipe() (Proxy-cached)
           → RecipeFactory.create() → Recipe entity
           → RecipeRepo.save()
```

## Estado de Implementación

| Archivo | Estado |
|---------|--------|
| `use_cases/process_receipt_usecase.py` | ✅ Completo — Pipeline orquestado |
| `use_cases/generate_recipe_usecase.py` | ✅ Completo — Factory + LLM invocation |
| `services/dashboard_metrics_service.py` | ✅ Completo — Métricas USD/CO₂ |
| `dtos/*.py` | ✅ Completo — Frozen dataclasses |

## Protocolo de Modificación

> Cuando agregues un nuevo Use Case:
> 1. Créalo en `use_cases/` programando SOLO contra interfaces de Domain.
> 2. Crea el DTO correspondiente en `dtos/`.
> 3. Registra las dependencias en `shared/dependency_container.py`.
> 4. Actualiza ESTE README con el nuevo flujo de datos.
