"""
DashboardMetricsService — computes economic & environmental impact metrics.

Aggregates data from repositories to produce ViewModels consumed by Streamlit.
Uses the Expiration Heap for urgency distribution and the Food Category Tree
for nutritional group breakdowns.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.interfaces.repository_interfaces import (
    FoodItemRepositoryInterface,
    RecipeRepositoryInterface,
)


@dataclass
class DashboardMetrics:
    """DTO for dashboard display."""

    total_items_tracked: int
    items_expiring_soon: int
    items_expired: int
    items_saved_by_recipes: int
    estimated_money_saved_usd: float
    estimated_co2_saved_kg: float
    category_distribution: dict[str, int]
    urgency_distribution: dict[str, int]


class DashboardMetricsService:
    """
    Application Service: aggregate metrics for the Streamlit dashboard.

    This is a read-only service — it queries repositories but never
    mutates domain entities.
    """

    # Average cost per food item (USD) — configurable
    AVG_ITEM_COST_USD: float = 3.50
    # Average CO2 per wasted food item (kg) — EPA estimate
    AVG_CO2_PER_ITEM_KG: float = 2.5

    def __init__(
        self,
        food_item_repo: FoodItemRepositoryInterface,
        recipe_repo: RecipeRepositoryInterface,
    ) -> None:
        self._food_item_repo = food_item_repo
        self._recipe_repo = recipe_repo

    def compute(self) -> DashboardMetrics:
        """Compute all dashboard metrics from current data."""
        all_items = self._food_item_repo.find_all()
        all_recipes = self._recipe_repo.find_all()

        expiring_soon = [i for i in all_items if i.urgency_level in ("CRITICAL", "WARNING")]
        expired = [i for i in all_items if i.is_expired]
        saved_count = sum(r.matched_expiring_count for r in all_recipes)

        # Category distribution from category_path
        cat_dist: dict[str, int] = {}
        for item in all_items:
            cat = item.category_path[0] if item.category_path else "Uncategorized"
            cat_dist[cat] = cat_dist.get(cat, 0) + 1

        # Urgency distribution
        urgency_dist: dict[str, int] = {}
        for item in all_items:
            level = item.urgency_level
            urgency_dist[level] = urgency_dist.get(level, 0) + 1

        return DashboardMetrics(
            total_items_tracked=len(all_items),
            items_expiring_soon=len(expiring_soon),
            items_expired=len(expired),
            items_saved_by_recipes=saved_count,
            estimated_money_saved_usd=saved_count * self.AVG_ITEM_COST_USD,
            estimated_co2_saved_kg=saved_count * self.AVG_CO2_PER_ITEM_KG,
            category_distribution=cat_dist,
            urgency_distribution=urgency_dist,
        )
