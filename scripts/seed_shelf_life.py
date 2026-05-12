"""
Seed Script — populate the shelf-life map into the database.

Run: python scripts/seed_shelf_life.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.shared.data_structures.shelf_life_map import ShelfLifeMap


def main() -> None:
    """Display all seeded shelf-life entries."""
    shelf_map = ShelfLifeMap()
    print(f"🌱 Shelf-Life Map initialized with {shelf_map.size} entries:\n")
    for item, days in sorted(shelf_map.all_items().items()):
        print(f"  {item:<20s} → {days:>3d} days")
    print(f"\n✅ Total: {shelf_map.size} food items seeded.")


if __name__ == "__main__":
    main()
