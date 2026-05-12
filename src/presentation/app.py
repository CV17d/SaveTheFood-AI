import streamlit as st
import os
import sys
from pathlib import Path
from datetime import date

# Add project root to path
sys.path.append(os.getcwd())

from src.shared.dependency_container import DependencyContainer
from src.shared.constants import OCR_STRATEGY_GEMINI_VISION
from src.application.use_cases.process_receipt_usecase import ProcessReceiptUseCase
from src.application.use_cases.generate_recipe_usecase import GenerateRecipeUseCase

def init_container():
    # Using the key provided in the context
    api_key = "AIzaSyA1lp7dMlwcKm76P0psFlJcicaRuH6G914"
    return DependencyContainer(
        gemini_api_key=api_key,
        gemini_model="gemini-1.5-flash-latest",
        ocr_strategy=OCR_STRATEGY_GEMINI_VISION
    )

def main():
    st.set_page_config(page_title="SaveTheFood AI - Demo", page_icon="🥗", layout="wide")
    
    st.title("🥗 SaveTheFood AI (Fase 2 Demo)")
    st.markdown("---")

    container = init_container()
    
    # Sidebar for Upload
    st.sidebar.header("📁 Ingesta de Recibos")
    uploaded_file = st.sidebar.file_uploader("Sube un recibo (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    if st.sidebar.button("Procesar Recibo") and uploaded_file:
        # Save temp file
        temp_path = Path("data/raw") / uploaded_file.name
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("Procesando con OCR e IA..."):
            use_case = ProcessReceiptUseCase(
                ocr_provider=container.ocr_provider(),
                receipt_repo=container.receipt_repository(),
                food_item_repo=container.food_item_repository(),
                llm_provider=container.llm_provider()
            )
            result = use_case.execute(str(temp_path))
            
            if not result.errors:
                st.success(f"¡Recibo procesado! Se extrajeron {result.items_extracted} productos.")
            else:
                st.error(f"Error: {result.errors[0]}")

    # Main Dashboard
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📦 Inventario Inteligente (Priorizado por Heap)")
        repo = container.food_item_repository()
        items = repo.find_all()
        
        if not items:
            st.info("El inventario está vacío. Sube un recibo para empezar.")
        else:
            # Simple table display
            data = []
            for item in sorted(items): # Uses FoodItem.__lt__ (Heap logic)
                data.append({
                    "Producto": item.name,
                    "Vence en": f"{item.days_until_expiration} días",
                    "Estado": item.urgency_level,
                    "Categoría": " → ".join(item.category_path)
                })
            st.table(data)

    with col2:
        st.subheader("🍳 Sugerencia de Receta")
        if st.button("Generar Receta Urgente"):
            with st.spinner("Gemini está cocinando una idea..."):
                recipe_use_case = GenerateRecipeUseCase(
                    llm_provider=container.llm_provider(),
                    food_item_repo=container.food_item_repository(),
                    recipe_repo=container.recipe_repository()
                )
                res = recipe_use_case.execute(max_ingredients=5)
                
                if res.recipe_id:
                    st.success(f"**{res.title}**")
                    st.write(f"Usando: {', '.join(res.ingredients_used)}")
                    st.info(f"Fuente: {res.source}")
                else:
                    st.warning("No hay suficientes ingredientes para una receta.")

if __name__ == "__main__":
    main()
