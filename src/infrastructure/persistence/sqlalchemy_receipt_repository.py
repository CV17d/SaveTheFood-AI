"""
SQLAlchemy Receipt Repository — concrete implementation of ReceiptRepositoryInterface.

Translates between Receipt domain entities and ReceiptModel ORM objects.
"""

from __future__ import annotations

import json
from datetime import datetime

from src.domain.entities.receipt import Receipt
from src.domain.interfaces.repository_interfaces import ReceiptRepositoryInterface
from src.infrastructure.persistence.database_session import DatabaseSession
from src.infrastructure.persistence.models import ReceiptModel


class SQLAlchemyReceiptRepository(ReceiptRepositoryInterface):
    """Concrete repository for Receipt persistence via SQLAlchemy."""

    def __init__(self, db_session: DatabaseSession) -> None:
        self._db = db_session

    def save(self, receipt: Receipt) -> None:
        with self._db.get_session() as session:
            model = self._to_model(receipt)
            session.merge(model)
            session.commit()

    def find_by_id(self, receipt_id: str) -> Receipt | None:
        with self._db.get_session() as session:
            model = session.get(ReceiptModel, receipt_id)
            return self._to_entity(model) if model else None

    def find_all(self) -> list[Receipt]:
        with self._db.get_session() as session:
            models = session.query(ReceiptModel).all()
            return [self._to_entity(m) for m in models]

    def delete(self, receipt_id: str) -> None:
        with self._db.get_session() as session:
            model = session.get(ReceiptModel, receipt_id)
            if model:
                session.delete(model)
                session.commit()

    # ─── Mappers ──────────────────────────────────────────

    @staticmethod
    def _to_model(entity: Receipt) -> ReceiptModel:
        return ReceiptModel(
            id=entity.id,
            image_path=str(entity.image_path),
            state=entity.state.value,
            raw_text="\n".join(entity.raw_text) if entity.raw_text else None,
            failure_reason=entity.failure_reason,
            uploaded_at=entity.uploaded_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def _to_entity(model: ReceiptModel) -> Receipt:
        from pathlib import Path
        from src.domain.entities.receipt import ReceiptState
        
        entity = Receipt(
            id=model.id,
            image_path=Path(model.image_path),
        )
        entity.state = ReceiptState(model.state)
        entity.raw_text = model.raw_text.split("\n") if model.raw_text else []
        entity.failure_reason = model.failure_reason
        entity.uploaded_at = model.uploaded_at
        entity.updated_at = model.updated_at
        return entity
