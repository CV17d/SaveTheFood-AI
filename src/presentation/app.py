import streamlit as st
import os
import sys
from pathlib import Path
from datetime import date
import pandas as pd

# Add project root to path
sys.path.append(os.getcwd())

from src.shared.dependency_container import DependencyContainer
from src.shared.constants import OCR_STRATEGY_GEMINI_VISION
from src.application.use_cases.process_receipt_usecase import ProcessReceiptUseCase
from src.application.use_cases.generate_recipe_usecase import GenerateRecipeUseCase
from src.application.services.dashboard_metrics_service import DashboardMetricsService

def init_container():
    # Using the working new key provided by the user
    api_key = "AIzaSyDk6Ts_sM1kym4yvthLeiuFYed0pp_csvQ"
    return DependencyContainer(
        gemini_api_key=api_key,
        gemini_model="gemini-flash-latest",
        ocr_strategy=OCR_STRATEGY_GEMINI_VISION
    )

def apply_custom_styles():
    st.markdown("""
        <style>
        .main {
            background-color: #f8f9fa;
        }
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            height: 3em;
            background-color: #2e7d32;
            color: white;
            font-weight: bold;
        }
        .stMetric {
            background-color: white;
            padding: 15px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .recipe-card {
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            border-left: 5px solid #2e7d32;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="SaveTheFood AI | Inteligencia Anti-Desperdicio",
        page_icon="🥗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    apply_custom_styles()
       container = init_container()
    metrics_service = DashboardMetricsService(
        container.food_item_repository(),
        container.recipe_repository()
    )
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3082/3082031.png", width=100)
        st.title("SaveTheFood AI")
        st.markdown("---")
        
        st.subheader("📸 Ingesta de Datos")
        uploaded_file = st.file_uploader("Escanea tu recibo", type=["jpg", "jpeg", "png"])
        
        if st.button("🚀 Procesar Recibo") and uploaded_file:
            temp_path = Path("data/raw") / uploaded_file.name
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            with st.spinner("Analizando con Visión Artificial..."):
                use_case = ProcessReceiptUseCase(
                    ocr_provider=container.ocr_provider(),
                    receipt_repo=container.receipt_repository(),
                    food_item_repo=container.food_item_repository(),
                    llm_provider=container.llm_provider()
                )
                result = use_case.execute(str(temp_path))
                if not result.errors:
                    st.success(f"¡Listo! {result.items_extracted} items nuevos.")
                    st.balloons()
                else:
                    st.error(f"Error: {result.errors[0]}")

    # --- MAIN CONTENT ---
    tab1, tab2, tab3 = st.tabs(["📦 Inventario", "🍳 Cocina AI", "📈 Impacto"])

    with tab1:
        st.header("Tu Despensa Inteligente")
        items = container.food_item_repository().find_all()
        
        if not items:
            st.info("Aún no tienes productos. ¡Sube un recibo para comenzar!")
        else:
            # Metrics Row
            m1, m2, m3 = st.columns(3)
            critical = len([i for i in items if i.urgency_level == "CRITICAL"])
            m1.metric("Items en Riesgo", critical, delta=critical, delta_color="inverse")
            m2.metric("Total Productos", len(items))
            m3.metric("Días Promedio Vida", "4.2")

            st.markdown("### Listado de Prioridad (Heap)")
            data = []
            for item in sorted(items):
                data.append({
                    "Producto": item.name,
                    "Vence en": f"{item.days_until_expiration} días",
                    "Urgencia": item.urgency_level,
                    "Categoría": " > ".join(item.category_path)
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.header("Chef AI: Zero Waste")
        st.markdown("Genera recetas creativas con lo que está por vencer.")
        
        col_btn, col_info = st.columns([1, 2])
        with col_btn:
            if st.button("✨ Generar Receta Mágica"):
                with st.spinner("Gemini está creando algo delicioso..."):
                    use_case = GenerateRecipeUseCase(
                        llm_provider=container.llm_provider(),
                        food_item_repo=container.food_item_repository(),
                        recipe_repo=container.recipe_repository()
                    )
                    res = use_case.execute(max_ingredients=5)
                    st.session_state.last_recipe = res

        if "last_recipe" in st.session_state:
            res = st.session_state.last_recipe
            if res.recipe_id:
                st.markdown(f"""
                <div class="recipe-card">
                    <h2>🍳 {res.title}</h2>
                    <p><b>Ingredientes Clave:</b> {', '.join(res.ingredients_used)}</p>
                    <p style="color: #666;"><i>Fuente: {res.source}</i></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Try to find the full recipe object to show details
                recipe_obj = container.recipe_repository().find_by_id(res.recipe_id)
                if recipe_obj:
                    col_ing, col_steps = st.columns(2)
                    with col_ing:
                        st.markdown("### Ingredientes")
                        for ing in recipe_obj.ingredients:
                            st.write(f"- {ing}")
                    with col_steps:
                        st.markdown("### Pasos")
                        for i, step in enumerate(recipe_obj.steps, 1):
                            st.write(f"{i}. {step}")
            else:
                st.error(res.title)

    with tab3:
        st.header("Tu Impacto Positivo")
        stats = metrics_service.compute()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Dinero Ahorrado", f"${stats.estimated_money_saved_usd:.2f}", "↑ 12%")
        c2.metric("CO₂ Mitigado", f"{stats.estimated_co2_saved_kg:.1f} kg", "↑ 5%")
        c3.metric("Items Salvados", stats.items_saved_by_recipes, "↑")
        
        st.info("Estas métricas se calculan basándose en los productos que consumes antes de su fecha de vencimiento.")
sumes antes de su fecha de vencimiento.")

if __name__ == "__main__":
    main()
