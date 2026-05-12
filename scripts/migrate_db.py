"""
Database Migration Script.

Creates all tables defined by SQLAlchemy ORM models.
Run: python scripts/migrate_db.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.infrastructure.persistence.database_session import DatabaseSession
from src.infrastructure.persistence.models import Base  # noqa: F401


def main() -> None:
    """Run database migrations (create tables)."""
    db_path = Path("data/db")
    db_path.mkdir(parents=True, exist_ok=True)

    db = DatabaseSession("sqlite:///data/db/savethefood.db")
    db.create_tables()
    print("✅ Database tables created successfully.")


if __name__ == "__main__":
    main()
