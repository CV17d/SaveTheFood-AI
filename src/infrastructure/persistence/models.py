"""
ORM Models — SQLAlchemy table definitions.

These are infrastructure-level models that map to database tables.
They are converted to/from domain entities in the repository layer.
Domain entities NEVER depend on these models (Dependency Rule).
"""

from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from src.infrastructure.persistence.database_session import Base


class ReceiptModel(Base):
    """SQLAlchemy model for the receipts table."""

    __tablename__ = "receipts"

    id = Column(String(36), primary_key=True)
    image_path = Column(String(512), nullable=False)
    state = Column(String(20), nullable=False, default="UPLOADED")
    raw_text = Column(Text, nullable=True)
    failure_reason = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class FoodItemModel(Base):
    """SQLAlchemy model for the food_items table."""

    __tablename__ = "food_items"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    quantity = Column(Float, default=1.0)
    unit = Column(String(20), default="units")
    purchase_date = Column(String(10), nullable=True)
    expiration_date = Column(String(10), nullable=True)
    category_path = Column(Text, nullable=True)  # JSON-serialized list
    confidence_score = Column(Float, default=1.0)
    receipt_id = Column(String(36), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())


class RecipeModel(Base):
    """SQLAlchemy model for the recipes table."""

    __tablename__ = "recipes"

    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    ingredients = Column(Text, nullable=True)  # JSON-serialized list
    steps = Column(Text, nullable=True)  # JSON-serialized list
    estimated_time_minutes = Column(Integer, default=30)
    servings = Column(Integer, default=2)
    tags = Column(Text, nullable=True)  # JSON-serialized list
    matched_expiring_count = Column(Integer, default=0)
    sustainability_score = Column(Float, default=0.0)
    source = Column(String(50), default="gemini_rag")
    generated_at = Column(DateTime, server_default=func.now())
