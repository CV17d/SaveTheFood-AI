"""
SQLAlchemy Food Repository — concrete implementation of FoodItemRepositoryInterface.

Translates between FoodItem domain entities and FoodItemModel ORM objects.
"""

from __future__ import annotations

import json

from src.domain.entities.food_item import FoodItem
from src.domain.interfaces.repository_interfaces import FoodItemRepositoryInterface
from src.infrastructure.persistence.database_session import DatabaseSession
from src.infrastructure.persistence.models import FoodItemModel


class SQLAlchemyFoodRepository(FoodItemRepositoryInterface):
    """Concrete repository for FoodItem persistence via SQLAlchemy."""

    def __init__(self, db_session: DatabaseSession) -> None:
        self._db = db_session

    def save(self, item: FoodItem) -> None:
        with self._db.get_session() as session:
            model = self._to_model(item)
            session.merge(model)
            session.commit()

    def save_batch(self, items: list[FoodItem]) -> None:
        with self._db.get_session() as session:
            for item in items:
                session.merge(self._to_model(item))
            session.commit()

    def find_by_id(self, item_id: str) -> FoodItem | None:
        with self._db.get_session() as session:
            model = session.get(FoodItemModel, item_id)
            return self._to_entity(model) if model else None

    def find_all(self) -> list[FoodItem]:
        with self._db.get_session() as session:
            models = session.query(FoodItemModel).all()
            return [self._to_entity(m) for m in models]

    def find_expiring_within(self, days: int) -> list[FoodItem]:
        """
        Find items expiring within N days.
        Optimized with SQL date comparison.
        """
        from datetime import date, timedelta
        
        target_date = date.today() + timedelta(days=days)
        
        with self._db.get_session() as session:
            # SQLite stores dates as ISO 8601 strings (YYYY-MM-DD), so string comparison works correctly
            models = session.query(FoodItemModel).filter(
                FoodItemModel.expiration_date != "None",
                FoodItemModel.expiration_date != None,
                FoodItemModel.expiration_date <= str(target_date),
                FoodItemModel.expiration_date >= str(date.today())
            ).all()
            
            return [self._to_entity(m) for m in models]

    def delete(self, item_id: str) -> None:
        with self._db.get_session() as session:
            model = session.get(FoodItemModel, item_id)
            if model:
                session.delete(model)
                session.commit()

    # ─── Mappers ──────────────────────────────────────────

    @staticmethod
    def _to_model(entity: FoodItem) -> FoodItemModel:
        return FoodItemModel(
            id=entity.id,
            name=entity.name,
            quantity=entity.quantity,
            unit=entity.unit,
            purchase_date=str(entity.purchase_date),
            expiration_date=str(entity.expiration_date) if entity.expiration_date else None,
            category_path=json.dumps(entity.category_path),
            confidence_score=entity.confidence_score,
            receipt_id=entity.receipt_id,
        )

    @staticmethod
    def _to_entity(model: FoodItemModel) -> FoodItem:
        from datetime import date

        exp_date = None
        if model.expiration_date and model.expiration_date != "None":
            exp_date = date.fromisoformat(model.expiration_date)

        purchase = date.today()
        if model.purchase_date and model.purchase_date != "None":
            purchase = date.fromisoformat(model.purchase_date)

        return FoodItem(
            id=model.id,
            name=model.name,
            quantity=model.quantity or 1.0,
            unit=model.unit or "units",
            purchase_date=purchase,
            expiration_date=exp_date,
            category_path=json.loads(model.category_path) if model.category_path else [],
            confidence_score=model.confidence_score or 1.0,
            receipt_id=model.receipt_id,
        )
