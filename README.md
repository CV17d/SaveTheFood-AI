# 🥗 SaveTheFood AI — Inteligencia Anti-Desperdicio

**SaveTheFood AI** es una solución integral diseñada para combatir el desperdicio de alimentos en el hogar utilizando Inteligencia Artificial avanzada (Google Gemini) y principios sólidos de ingeniería de software.

---

## 📖 ¿Qué hace el programa actualmente?

El sistema permite a los usuarios gestionar su inventario de alimentos de manera inteligente mediante las siguientes funciones:

1.  **📸 Ingesta por Visión (OCR + IA)**: El usuario sube una imagen de un recibo de supermercado. El sistema utiliza **Gemini Vision** para extraer automáticamente los productos.
2.  **⏳ Estimación Inteligente de Vencimiento**: Para cada producto, el sistema consulta un **Hashmap de Vida Útil** (O(1)) o utiliza la **IA** para estimar cuántos días le quedan de vida útil.
3.  **📦 Inventario Priorizado (Heap)**: Los productos se organizan automáticamente mediante un **Min-Heap**, mostrando siempre en primer lugar los alimentos que están más cerca de vencer.
4.  **🍳 Generador de Recetas Zero-Waste**: Utiliza un motor de **Generación Aumentada por Recuperación (RAG)** para sugerir recetas creativas en español que aprovechan los ingredientes más urgentes del inventario.
5.  **📈 Dashboard de Impacto**: Visualiza el ahorro económico (USD) y ambiental (CO₂) logrado al consumir los alimentos antes de que se desperdicien.

---

## 🛠️ Tecnologías y Algoritmos (Puntos Técnicos Clave)

El proyecto destaca por su robustez técnica:
-   **Arquitectura**: Clean Architecture (4 capas) para una separación total de responsabilidades.
-   **IA**: Integración con **Gemini 2.0 Flash** para procesamiento de lenguaje natural y visión artificial.
-   **Estructuras de Datos Implementadas**:
    -   **Min-Heap**: Para la priorización de caducidad.
    -   **Hashmap**: Para búsqueda instantánea de vida útil.
    -   **Queue**: Para el pipeline de procesamiento de recibos.
    -   **N-ary Tree**: Para la taxonomía jerárquica de categorías.
    -   **Grafo Bipartito**: Para conectar ingredientes con recetas sugeridas.
    -   **Stack**: Para la funcionalidad de "Deshacer" en correcciones manuales.

---

## 🚀 Guía de Ejecución (Para el Profesor)

Siga estos pasos para poner en marcha la aplicación en un entorno local:

### 1. Prerrequisitos
-   Python 3.11 o superior instalado.
-   Una clave de API de Google Gemini (ya configurada por defecto en el código para esta entrega).

### 2. Configuración del Entorno
Desde la raíz del proyecto, ejecute:
```powershell
# Instalar dependencias necesarias
pip install streamlit google-generativeai sqlalchemy pandas pillow
```

### 3. Ejecutar la Aplicación
Para iniciar el Dashboard interactivo, ejecute el siguiente comando:
```powershell
python -m streamlit run src/presentation/app.py
```

### 4. Cómo Probar el Sistema
1.  **Cargar Inventario**: Use la barra lateral para subir una imagen de un recibo (hay ejemplos en la carpeta `data/raw`). Pulse **"🚀 Procesar Recibo"**.
2.  **Ver Prioridades**: En la pestaña **📦 Inventario**, verá los productos ordenados por urgencia.
3.  **Cocinar con IA**: Vaya a la pestaña **🍳 Cocina AI** y pulse **"✨ Generar Receta Mágica"**. Gemini le sugerirá una receta basada en sus productos próximos a vencer.
4.  **Métricas**: Revise la pestaña **📈 Impacto** para ver las estadísticas de ahorro.

---

## 📁 Estructura del Código
-   `src/domain`: El núcleo del negocio (Entidades, Interfaces).
-   `src/application`: Casos de uso (Lógica del pipeline y recetas).
-   `src/infrastructure`: Implementaciones de IA, OCR y Persistencia (SQLite).
-   `src/presentation`: Interfaz de usuario con Streamlit.
-   `src/shared`: Estructuras de datos personalizadas y contenedor de dependencias.

---
*Desarrollado como parte del proyecto de Inteligencia Artificial y Algoritmos Avanzados.*
