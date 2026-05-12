"""
RecipeGraph — Bipartite Graph Data Structure.

Connects Ingredient nodes to Recipe nodes. Finds recipes maximizing
coverage of expiring ingredients.

Complexity: add O(1), find_best O(|R|×|I_exp|), get_neighbors O(1).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass
class IngredientNode:
    name: str
    is_expiring: bool = False
    days_remaining: int | None = None


@dataclass
class RecipeNode:
    recipe_id: str
    title: str
    score: float = 0.0


class RecipeGraph:
    """Bipartite Graph: Ingredients ↔ Recipes via adjacency lists."""

    def __init__(self) -> None:
        self._ing_to_rec: dict[str, set[str]] = defaultdict(set)
        self._rec_to_ing: dict[str, set[str]] = defaultdict(set)
        self._ingredients: dict[str, IngredientNode] = {}
        self._recipes: dict[str, RecipeNode] = {}

    def add_ingredient(self, node: IngredientNode) -> None:
        self._ingredients[node.name.lower()] = node

    def add_recipe(self, node: RecipeNode) -> None:
        self._recipes[node.recipe_id] = node

    def add_edge(self, ingredient_name: str, recipe_id: str) -> None:
        key = ingredient_name.lower()
        self._ing_to_rec[key].add(recipe_id)
        self._rec_to_ing[recipe_id].add(key)

    def get_recipes_for(self, ingredient: str) -> set[str]:
        return self._ing_to_rec.get(ingredient.lower(), set())

    def get_ingredients_for(self, recipe_id: str) -> set[str]:
        return self._rec_to_ing.get(recipe_id, set())

    def find_best_recipe(self, expiring: list[str]) -> str | None:
        exp_set = {i.lower() for i in expiring}
        best_id, best_n = None, 0
        for rid, ings in self._rec_to_ing.items():
            n = len(ings & exp_set)
            if n > best_n:
                best_n, best_id = n, rid
        return best_id

    def rank_recipes(self, expiring: list[str]) -> list[tuple[str, int]]:
        exp_set = {i.lower() for i in expiring}
        ranked = [
            (rid, len(ings & exp_set))
            for rid, ings in self._rec_to_ing.items()
            if len(ings & exp_set) > 0
        ]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked

    @property
    def ingredient_count(self) -> int:
        return len(self._ingredients)

    @property
    def recipe_count(self) -> int:
        return len(self._recipes)

    def __repr__(self) -> str:
        return f"RecipeGraph(ingredients={self.ingredient_count}, recipes={self.recipe_count})"
