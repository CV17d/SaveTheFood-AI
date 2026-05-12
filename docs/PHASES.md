# 🗺️ Plan de Fases — SaveTheFood AI

> **Directiva:** Este documento define los entregables técnicos granulares para cada fase
> de desarrollo. Cada tarea incluye el archivo específico, la acción requerida, y el
> criterio de aceptación.

---

## Estado General

| Fase | Responsable | Estado | Entregables |
|------|-------------|--------|-------------|
| **Fase 1** — Core & Ingestion | Arquitecto (Completada) | ✅ Finalizada | Arquitectura, interfaces, DI, EDs, tests unitarios |
| **Fase 2** — Intelligence Engine | Desarrollador B | 🔲 Pendiente | OCR real, Gemini API, lógica de EDs en pipeline |
| **Fase 3** — Dashboard & UI | Desarrollador C | 🔲 Pendiente | Streamlit, Plotly, ViewModels, tests E2E |

---

## Fase 1 — Core & Ingestion ✅ COMPLETADA

### Entregables Finalizados

- [x] Arquitectura Clean Architecture (4 capas) con Dependency Rule
- [x] Domain entities con State Pattern (Receipt), heap ordering (FoodItem)
- [x] Value Objects inmutables (ExpirationDate, NutritionalInfo)
- [x] Jerarquía de excepciones de dominio
- [x] 3 interfaces/ports (OCR, LLM, Repository)
- [x] 6 estructuras de datos implementadas y documentadas
- [x] DI Container con Strategy + Proxy wiring
- [x] Use Cases orquestadores (ProcessReceipt, GenerateRecipe)
- [x] Application Services (DashboardMetrics)
- [x] DTOs frozen para desacoplamiento
- [x] SQLAlchemy ORM models + session manager + food repository
- [x] Proxy Pattern para cache de API (GeminiCacheProxy)
- [x] Tests unitarios: 7 data structures + State Pattern lifecycle
- [x] Configuración: pyproject.toml, Makefile, Dockerfile, docker-compose
- [x] Documentación: README_AI.md, sub-READMEs por capa

---

## Fase 2 — Intelligence Engine 🔧 PENDIENTE

### 2.1 OCR Real — PyTesseract Adapter

**Archivo:** `src/infrastructure/ocr/pytesseract_adapter.py`
**Acción:** Reemplazar `NotImplementedError` con lógica funcional.

**Tareas específicas:**

- [ ] Instalar y configurar `pytesseract` y `opencv-python` en el entorno.
- [ ] Implementar preprocessing de imagen con OpenCV:
  - Cargar imagen con `cv2.imread()`.
  - Convertir a escala de grises: `cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)`.
  - Aplicar threshold adaptativo: `cv2.adaptiveThreshold()`.
  - Opcional: deskew, denoise, crop de márgenes.
- [ ] Extraer texto con `pytesseract.image_to_string()`.
- [ ] Retornar `List[str]` de líneas de texto (una por bounding box).
- [ ] Manejar excepciones y lanzar `OCRExtractionError` en caso de fallo.

**Criterio de aceptación:** Procesar exitosamente 3 imágenes de recibos de prueba
y extraer al menos el 70% de los productos legibles.

---

### 2.2 Gemini LLM Provider

**Archivo:** `src/infrastructure/ai/gemini_llm_provider.py`
**Acción:** Implementar `generate_recipe()` y `estimate_shelf_life()`.

**Tareas específicas:**

- [ ] Inicializar cliente Gemini: `google.generativeai.configure(api_key=...)`.
- [ ] Diseñar prompt estructurado para `generate_recipe()`:
  - Input: lista de ingredientes + constraints opcionales.
  - Output esperado: JSON con `title`, `description`, `ingredients`, `steps`, `tags`.
  - Incluir system prompt con rol de chef experto en reducción de desperdicio.
- [ ] Parsear respuesta JSON del LLM y manejar malformed responses.
- [ ] Implementar `estimate_shelf_life()`:
  - Prompt: "¿Cuántos días dura {item_name} después de la compra?"
  - Extraer número entero de la respuesta.
- [ ] Integrar con `GeminiCacheProxy` (ya implementado — solo verificar wiring).

**Criterio de aceptación:** Generar una receta válida con JSON parseable a partir
de 5 ingredientes de ejemplo. Shelf-life estimation retorna enteros razonables.

---

### 2.3 Integración de Estructuras de Datos en el Pipeline

**Archivos:** `process_receipt_usecase.py`, `generate_recipe_usecase.py`

**Tareas específicas:**

- [ ] Integrar `ProcessingQueue` en `ProcessReceiptUseCase`:
  - Encolar imágenes al recibir múltiples uploads.
  - Desencolar y procesar en orden FIFO.
- [ ] Integrar `ShelfLifeMap` en el parsing de FoodItems:
  - Buscar cada item en el hashmap (O(1)).
  - Si no existe, invocar `LLMProvider.estimate_shelf_life()` como fallback.
  - Almacenar resultado en `FoodItem.expiration_date`.
- [ ] Integrar `ExpirationHeap` en `GenerateRecipeUseCase`:
  - Construir heap desde items del repositorio.
  - Extraer top-N más urgentes con `extract_top_n()`.
- [ ] Integrar `FoodCategoryTree`:
  - Insertar cada FoodItem en su categoría al parsear.
  - Almacenar `category_path` en el entity.
- [ ] Integrar `RecipeGraph`:
  - Construir grafo bipartito desde recetas del repositorio.
  - Usar `find_best_recipe()` para ranking antes de invocación LLM.

**Criterio de aceptación:** Pipeline end-to-end funcional: imagen → OCR → items
con vencimiento estimado → receta generada priorizando ingredientes urgentes.

---

### 2.4 Persistencia Completa

**Archivos:** `sqlalchemy_food_repository.py`, nuevo `sqlalchemy_receipt_repository.py`

**Tareas específicas:**

- [ ] Implementar `SQLAlchemyReceiptRepository` (actualmente solo existe `FoodRepository`).
- [ ] Implementar `SQLAlchemyRecipeRepository`.
- [ ] Optimizar `find_expiring_within()` con filtro SQL en lugar de in-memory.
- [ ] Registrar nuevos repositorios en `DependencyContainer`.

**Criterio de aceptación:** Todas las operaciones CRUD persisten y recuperan datos
correctamente. Tests de integración pasan con SQLite en memoria.

---

### 2.5 Tests de Integración

**Archivo:** `tests/integration/test_ocr_pipeline.py`

- [ ] Test: PyTesseract extrae texto de imagen de recibo real.
- [ ] Test: ShelfLifeMap retorna datos correctos para items conocidos.
- [ ] Test: Pipeline completo Process Receipt con DB en memoria.
- [ ] Test: GeminiCacheProxy sirve resultados cacheados correctamente.

---

## Fase 3 — Dashboard & Final Polish 🔧 PENDIENTE

### 3.1 Streamlit Application Setup

**Archivo:** `src/presentation/app.py`

**Tareas específicas:**

- [ ] Configurar `st.set_page_config()` con título, ícono, layout wide.
- [ ] Inicializar `DependencyContainer` desde `config/settings.py`.
- [ ] Implementar navegación multipage con `st.navigation()`.
- [ ] Crear estado de sesión para el `UndoStack` y `ProcessingQueue`.

---

### 3.2 Sidebar Component

**Archivo:** `src/presentation/components/sidebar.py`

- [ ] Widget de upload de imagen (`st.file_uploader`).
- [ ] Selector de estrategia OCR (PyTesseract vs. Gemini Vision).
- [ ] Indicador de estado del receipt (badges por estado del State Pattern).
- [ ] Botón de procesamiento con spinner.

---

### 3.3 Inventory Page

**Archivo:** `src/presentation/pages/inventory.py`

- [ ] Tabla de inventario alimentario ordenada por vencimiento (datos del Heap).
- [ ] Badges de urgencia con colores: 🔴 CRITICAL, 🟡 WARNING, 🟢 OK, ⚫ EXPIRED.
- [ ] Edición inline de items (nombre, cantidad) con corrección manual de OCR.
- [ ] Integrar `UndoStack`: botón "Deshacer" que revierte la última corrección.
- [ ] Mostrar historial de acciones del stack.

---

### 3.4 Charts Component — Plotly

**Archivo:** `src/presentation/components/charts.py`

- [ ] **Sunburst/Treemap:** Categorías alimentarias desde `FoodCategoryTree.to_dict()`.
- [ ] **Gauge:** Porcentaje de alimentos salvados vs. desperdiciados.
- [ ] **Bar chart:** Distribución de urgencia (CRITICAL/WARNING/OK/EXPIRED).
- [ ] **Timeline:** Proyección de vencimientos en los próximos 14 días.
- [ ] **KPI Cards:** Total items, dinero ahorrado (USD), CO₂ evitado (kg).

---

### 3.5 Recipes Page

**Archivo:** `src/presentation/pages/recipes.py`

- [ ] Cards de recetas generadas con título, descripción, tiempo, porciones.
- [ ] Lista de ingredientes con badges de "expiring soon".
- [ ] Botón "Generar Nueva Receta" con constraints (vegetariana, rápida, etc.).
- [ ] Visualización del `RecipeGraph` (networkx + Plotly network graph).

---

### 3.6 ViewModels

**Archivo:** `src/presentation/view_models/inventory_viewmodel.py`

- [ ] Transformar `FoodItem` entities → `FoodItemDTO` para la tabla.
- [ ] Computar métricas desde `DashboardMetricsService`.
- [ ] Formatear fechas, urgencias, y categorías para display.

---

### 3.7 Tests End-to-End

**Archivo:** `tests/e2e/test_full_pipeline.py`

- [ ] Test: Upload de imagen → OCR → items en DB → receta generada.
- [ ] Test: Edición manual de item → UndoStack tiene la acción → Undo revierte.
- [ ] Test: Dashboard metrics muestra datos coherentes con el inventario.

---

## Protocolo de Commits — Conventional Commits (Estricto)

### Formato

```
<tipo>(<scope>): <descripción corta>

[cuerpo opcional]
[footer opcional]
```

### Tipos Permitidos

| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Documentación |
| `test` | Tests |
| `refactor` | Refactorización sin cambio funcional |
| `chore` | Configuración, CI/CD, dependencias |
| `style` | Formateo, sin cambio de lógica |

### Primeros 5 Commits Sugeridos (Fase 1)

```
1. chore: initialize project structure and configuration files
2. feat(domain): implement entities, value objects, and interfaces
3. feat(shared): implement 6 advanced data structures with tests
4. feat(application): implement use cases, services, and DTOs
5. feat(infrastructure): implement persistence layer and cache proxy
```

### Commits Sugeridos para Fase 2

```
6. feat(infrastructure): implement PyTesseract OCR adapter
7. feat(infrastructure): implement Gemini LLM provider with prompt engineering
8. feat(application): integrate data structures into processing pipeline
9. feat(infrastructure): implement receipt and recipe repositories
10. test(integration): add OCR pipeline integration tests
```

### Commits Sugeridos para Fase 3

```
11. feat(presentation): implement Streamlit multipage app with sidebar
12. feat(presentation): implement inventory page with heap view and undo stack
13. feat(presentation): implement Plotly charts and dashboard metrics
14. feat(presentation): implement recipes page with graph visualization
15. test(e2e): add end-to-end pipeline tests
```

---

## Directiva de Documentación por Avance

> **REGLA INVIOLABLE:** Cada vez que se complete un caso de uso, un adapter,
> o un módulo de infraestructura, el desarrollador **DEBE**:
>
> 1. Actualizar el `README.md` de la carpeta correspondiente marcando ✅.
> 2. Actualizar la sección "Estado Actual" del `README_AI.md`.
> 3. Actualizar ESTE archivo (`PHASES.md`) marcando la tarea como `[x]`.
> 4. Hacer commit con el formato Conventional Commits.
>
> **Penalización por incumplimiento:** El PR será rechazado hasta que
> se adjunte la documentación correspondiente.
