"""
FoodCategoryTree — N-ary Tree Data Structure.

PURPOSE:
    Categorizes food items in a hierarchical taxonomy for nutritional
    grouping and dashboard analytics. Example hierarchy:
        Food
        ├── Dairy
        │   ├── Milk
        │   ├── Cheese
        │   │   ├── Cheddar
        │   │   └── Mozzarella
        │   └── Yogurt
        ├── Produce
        │   ├── Fruits
        │   └── Vegetables
        └── Proteins
            ├── Beef
            ├── Chicken
            └── Fish

WHERE USED:
    - src/application/services/dashboard_metrics_service.py → Category distribution.
    - src/presentation/components/charts.py → Treemap / Sunburst visualizations.
    - src/domain/entities/food_item.py → category_path field.

COMPLEXITY:
    - insert():       O(D) where D = depth of the path
    - search():       O(D)
    - get_children(): O(1)
    - traverse():     O(N) where N = total nodes

WHY:
    An N-ary tree naturally models hierarchical food categorization.
    It enables grouped aggregation (e.g., "How many Dairy items are
    expiring?") and powers interactive sunburst/treemap charts.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TreeNode:
    """A single node in the Food Category Tree."""

    name: str
    children: dict[str, TreeNode] = field(default_factory=dict)
    item_count: int = 0
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0


class FoodCategoryTree:
    """
    N-ary Tree for hierarchical food categorization.

    The tree is rooted at a virtual "Food" node. Each level represents
    a more specific category (e.g., Food → Dairy → Cheese → Cheddar).
    """

    def __init__(self) -> None:
        self._root = TreeNode(name="Food")

    @property
    def root(self) -> TreeNode:
        return self._root

    def insert(self, category_path: list[str]) -> TreeNode:
        """
        Insert a category path into the tree. O(D).

        Args:
            category_path: List of category names from general to specific,
                           e.g., ["Dairy", "Cheese", "Cheddar"].

        Returns:
            The leaf TreeNode at the end of the path.
        """
        current = self._root
        for category in category_path:
            if category not in current.children:
                current.children[category] = TreeNode(name=category)
            current = current.children[category]
            current.item_count += 1
        return current

    def search(self, category_path: list[str]) -> TreeNode | None:
        """
        Search for a node by category path. O(D).

        Returns:
            The TreeNode if found, None otherwise.
        """
        current = self._root
        for category in category_path:
            if category not in current.children:
                return None
            current = current.children[category]
        return current

    def get_children(self, category_path: list[str] | None = None) -> list[str]:
        """
        Get child category names at a given path. O(1).

        Args:
            category_path: Path to the parent node (None = root).

        Returns:
            List of child category names.
        """
        if category_path is None:
            return list(self._root.children.keys())

        node = self.search(category_path)
        return list(node.children.keys()) if node else []

    def traverse_dfs(self, node: TreeNode | None = None, depth: int = 0) -> list[tuple[str, int, int]]:
        """
        Depth-first traversal of the tree. O(N).

        Returns:
            List of (name, depth, item_count) tuples.
        """
        if node is None:
            node = self._root

        result: list[tuple[str, int, int]] = [(node.name, depth, node.item_count)]
        for child in node.children.values():
            result.extend(self.traverse_dfs(child, depth + 1))
        return result

    def to_dict(self, node: TreeNode | None = None) -> dict:
        """Convert the tree to a nested dictionary (for JSON serialization)."""
        if node is None:
            node = self._root

        return {
            "name": node.name,
            "count": node.item_count,
            "children": [self.to_dict(child) for child in node.children.values()],
        }

    def __repr__(self) -> str:
        total = sum(1 for _ in self.traverse_dfs()) - 1  # Exclude root
        return f"FoodCategoryTree(categories={total})"
