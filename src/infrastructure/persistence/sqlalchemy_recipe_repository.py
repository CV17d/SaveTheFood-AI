"""
SQLAlchemy Recipe Repository — concrete implementation of RecipeRepositoryInterface.

Translates between Recipe domain entities and RecipeModel ORM objects.
"""

from __future__ import annotations

import json
from datetime import datetime

from src.domain.entities.recipe import Recipe
from src.domain.interfaces.repository_interfaces import RecipeRepositoryInterface
from src.infrastructure.persistence.database_session import DatabaseSession
from src.infrastructure.persistence.models import RecipeModel


class SQLAlchemyRecipeRepository(RecipeRepositoryInterface):
    """Concrete repository for Recipe persistence via SQLAlchemy."""

    def __init__(self, db_session: DatabaseSession) -> None:
        self._db = db_session

    def save(self, recipe: Recipe) -> None:
        with self._db.get_session() as session:
            model = self._to_model(recipe)
            session.merge(model)
            session.commit()

    def find_by_id(self, recipe_id: str) -> Recipe | None:
        with self._db.get_session() as session:
            model = session.get(RecipeModel, recipe_id)
            return self._to_entity(model) if model else None

    def find_all(self) -> list[Recipe]:
        with self._db.get_session() as session:
            models = session.query(RecipeModel).all()
            return [self._to_entity(m) for m in models]

    def find_by_ingredient(self, ingredient: str) -> list[Recipe]:
        with self._db.get_session() as session:
            # We search if the JSON string contains the ingredient string.
            # This is a simple approach. For advanced use, PostgreSQL JSONB would be better,
            # but this works for SQLite with JSON strings.
            models = session.query(RecipeModel).filter(RecipeModel.ingredients.like(f"%{ingredient}%")).all()
            return [self._to_entity(m) for m in models]

    # ─── Mappers ──────────────────────────────────────────

    @staticmethod
    def _to_model(entity: Recipe) -> RecipeModel:
        return RecipeModel(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            ingredients=json.dumps(entity.ingredients),
            steps=json.dumps(entity.steps),
            estimated_time_minutes=entity.estimated_time_minutes,
            servings=entity.servings,
            tags=json.dumps(entity.tags),
            matched_expiring_count=entity.matched_expiring_count,
            sustainability_score=entity.sustainability_score,
            source=entity.source,
            generated_at=entity.generated_at,
        )

    @staticmethod
    def _to_entity(model: RecipeModel) -> Recipe:
        entity = Recipe(
            id=model.id,
            title=model.title,
            description=model.description,
            ingredients=json.loads(model.ingredients) if model.ingredients else [],
            steps=json.loads(model.steps) if model.steps else [],
            estimated_time_minutes=model.estimated_time_minutes,
            servings=model.servings,
            tags=json.loads(model.tags) if model.tags else [],
        )
        entity.matched_expiring_count = model.matched_expiring_count
        entity.sustainability_score = model.sustainability_score
        entity.source = model.source
        entity.generated_at = model.generated_at
        return entity
