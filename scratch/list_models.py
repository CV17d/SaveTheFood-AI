import google.generativeai as genai

api_key = "AIzaSyDk6Ts_sM1kym4yvthLeiuFYed0pp_csvQ"
genai.configure(api_key=api_key)

print("--- Modelos disponibles para esta API Key ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error al listar modelos: {e}")
