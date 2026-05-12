"""
Database Session — SQLAlchemy engine and session factory.

Provides a centralized database connection managed by the DI container.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""

    pass


class DatabaseSession:
    """
    Manages SQLAlchemy engine and session lifecycle.

    Usage:
        db = DatabaseSession("sqlite:///data/db/savethefood.db")
        db.create_tables()
        with db.get_session() as session:
            session.add(...)
            session.commit()
    """

    def __init__(self, database_url: str) -> None:
        self._engine = create_engine(database_url, echo=False)
        self._session_factory = sessionmaker(bind=self._engine)

    def create_tables(self) -> None:
        """Create all tables defined by ORM models."""
        Base.metadata.create_all(self._engine)

    def get_session(self) -> Session:
        """Create a new database session."""
        return self._session_factory()

    def drop_tables(self) -> None:
        """Drop all tables (for testing only)."""
        Base.metadata.drop_all(self._engine)
