import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from src.shared.dependency_container import DependencyContainer

def test_ai():
    print("--- Testing SaveTheFood AI Intelligence ---")
    
    # Initialize container (using the new API key)
    api_key = "AIzaSyDk6Ts_sM1kym4yvthLeiuFYed0pp_csvQ"
    
    container = DependencyContainer(
        gemini_api_key=api_key,
        gemini_model="gemini-flash-latest"
    )
    
    llm = container.llm_provider()
    
    print(f"\n1. Testing Shelf-Life Estimation for 'Dragon Fruit'...")
    days = llm.estimate_shelf_life("Dragon Fruit")
    print(f"Result: {days} days")
    
    print(f"\n2. Testing Recipe Generation for [Milk, Eggs, Spinach, Chicken]...")
    ingredients = ["Milk", "Eggs", "Spinach", "Chicken"]
    try:
        recipe = llm.generate_recipe(ingredients)
        print("\nRecipe Generated Successfully:")
        print(f"Title: {recipe.get('title')}")
        print(f"Time: {recipe.get('estimated_time_minutes')} mins")
        print(f"Description: {recipe.get('description')}")
        print("\nIngredients used in recipe:")
        for ing in recipe.get('ingredients', []):
            print(f"- {ing}")
    except Exception as e:
        print(f"Error generating recipe: {e}")

if __name__ == "__main__":
    test_ai()
