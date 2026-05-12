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
            state=entity.state.name,
            raw_text="\n".join(entity.raw_text_lines) if entity.raw_text_lines else None,
            failure_reason=entity.failure_reason,
            uploaded_at=entity.uploaded_at,
            # updated_at is handled by SQLAlchemy server_default/onupdate
        )

    @staticmethod
    def _to_entity(model: ReceiptModel) -> Receipt:
        from src.domain.entities.receipt import (
            ReceiptState, 
            UploadedState, ProcessingState, ParsedState, FailedState, CompletedState
        )
        
        entity = Receipt(
            id=model.id,
            image_path=str(model.image_path),
            uploaded_at=model.uploaded_at,
        )
        
        # Restore raw text lines
        entity.raw_text_lines = model.raw_text.split("\n") if model.raw_text else []
        
        # Restore State Pattern internal state
        state_enum = ReceiptState[model.state] if isinstance(model.state, str) else ReceiptState.UPLOADED
        entity._state = state_enum
        
        # Restore appropriate state handler
        handlers = {
            ReceiptState.UPLOADED: UploadedState,
            ReceiptState.PROCESSING: ProcessingState,
            ReceiptState.PARSED: ParsedState,
            ReceiptState.FAILED: FailedState,
            ReceiptState.COMPLETED: CompletedState,
        }
        handler_class = handlers.get(state_enum, UploadedState)
        entity._state_handler = handler_class()
        
        entity._failure_reason = model.failure_reason
        
        return entity
