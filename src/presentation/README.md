# 🖥️ Presentation Layer — Interfaz de Usuario

> **Responsabilidad:** Renderizar la interfaz de usuario usando Streamlit y Plotly.
> Consume SOLO DTOs de la capa Application. NUNCA importa entidades del Domain
> ni clases concretas de Infrastructure.

## Responsabilidades

1. **App** — Entrypoint de Streamlit, configuración de páginas, inicialización del DI container.
2. **Components** — Componentes reutilizables de UI (sidebar, charts).
3. **Pages** — Vistas de página completas (inventario, recetas).
4. **ViewModels** — Transformadores de datos Domain → formato de UI.

## Estructura de Archivos

```
presentation/
├── __init__.py
├── app.py                              ← Streamlit entrypoint (multipage)
├── components/
│   ├── __init__.py
│   ├── sidebar.py                      ← Navegación + upload de recibos
│   └── charts.py                       ← Plotly: sunburst, treemap, gauges
├── pages/
│   ├── __init__.py
│   ├── inventory.py                    ← Vista de inventario (Heap + Undo Stack)
│   └── recipes.py                      ← Recetas AI (Graph visualization)
└── view_models/
    ├── __init__.py
    └── inventory_viewmodel.py          ← Domain entities → UI-ready dicts
```

## Estructuras de Datos Integradas en la UI

| ED | Componente | Uso |
|----|-----------|-----|
| **ExpirationHeap** | `pages/inventory.py` | Muestra items ordenados por urgencia de vencimiento |
| **UndoStack** | `pages/inventory.py` | Botón "Deshacer" para correcciones manuales de OCR |
| **FoodCategoryTree** | `components/charts.py` | Plotly Sunburst/Treemap de categorías alimentarias |
| **RecipeGraph** | `pages/recipes.py` | Visualización del grafo bipartito ingredientes↔recetas |

## Estado de Implementación

| Archivo | Estado | Fase |
|---------|--------|------|
| `app.py` | 🔧 Stub | Fase 3 |
| `components/sidebar.py` | 🔧 Stub | Fase 3 |
| `components/charts.py` | 🔧 Stub | Fase 3 |
| `pages/inventory.py` | 🔧 Stub | Fase 3 |
| `pages/recipes.py` | 🔧 Stub | Fase 3 |
| `view_models/inventory_viewmodel.py` | 🔧 Stub | Fase 3 |

## Protocolo de Modificación

> Al implementar una página o componente:
> 1. Importa SOLO DTOs de `src/application/dtos/` y servicios de `src/application/services/`.
> 2. Usa `DependencyContainer` para resolver dependencias (inyección, no instanciación directa).
> 3. Agrega IDs únicos a todos los elementos interactivos para testing E2E.
> 4. Actualiza ESTE README marcando el archivo como ✅ Completo.
