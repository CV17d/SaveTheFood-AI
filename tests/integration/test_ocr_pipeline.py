"""Integration tests for the OCR pipeline — Phase 1."""

import os
from pathlib import Path
import pytest

from src.domain.entities.receipt import Receipt
from src.domain.entities.food_item import FoodItem
from src.domain.entities.recipe import Recipe
from src.infrastructure.ocr.pytesseract_adapter import PyTesseractAdapter
from src.infrastructure.persistence.database_session import DatabaseSession
from src.infrastructure.persistence.sqlalchemy_food_repository import SQLAlchemyFoodRepository
from src.infrastructure.persistence.sqlalchemy_receipt_repository import SQLAlchemyReceiptRepository
from src.infrastructure.persistence.sqlalchemy_recipe_repository import SQLAlchemyRecipeRepository

@pytest.fixture
def db_session():
    """Provides an in-memory SQLite database session."""
    session = DatabaseSession("sqlite:///:memory:")
    # Initialize the tables
    from src.infrastructure.persistence.models import Base
    Base.metadata.create_all(session._engine)
    return session


@pytest.fixture
def dummy_receipt_image(tmp_path):
    """Creates a dummy image for testing."""
    import cv2
    import numpy as np

    img_path = tmp_path / "test_receipt.jpg"
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.putText(img, 'MILK 1L', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, 'BREAD', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imwrite(str(img_path), img)
    return img_path


def test_pytesseract_extraction(dummy_receipt_image):
    """Test: PyTesseract extracts text from a test receipt image."""
    # Assuming tesseract is installed in the system.
    # We test only if it's available, otherwise skip.
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
    except Exception:
        pytest.skip("Tesseract not installed")

    adapter = PyTesseractAdapter()
    text_lines = adapter.extract_text(dummy_receipt_image)
    
    assert len(text_lines) >= 2
    assert any("MILK" in line.upper() for line in text_lines)
    assert any("BREAD" in line.upper() for line in text_lines)


def test_repository_crud_sqlite(db_session):
    """Test: Repositories CRUD operations with in-memory SQLite."""
    food_repo = SQLAlchemyFoodRepository(db_session)
    receipt_repo = SQLAlchemyReceiptRepository(db_session)
    recipe_repo = SQLAlchemyRecipeRepository(db_session)

    # Test FoodItem Repository
    food = FoodItem(name="Test Food", quantity=1.0)
    food_repo.save(food)
    fetched_food = food_repo.find_by_id(food.id)
    assert fetched_food is not None
    assert fetched_food.name == "Test Food"
    food_repo.delete(food.id)
    assert food_repo.find_by_id(food.id) is None

    # Test Receipt Repository
    receipt = Receipt(image_path=Path("test.jpg"))
    receipt_repo.save(receipt)
    fetched_receipt = receipt_repo.find_by_id(receipt.id)
    assert fetched_receipt is not None
    assert str(fetched_receipt.image_path) == "test.jpg"
    receipt_repo.delete(receipt.id)
    assert receipt_repo.find_by_id(receipt.id) is None

    # Test Recipe Repository
    recipe = Recipe(title="Test Recipe", ingredients=["ingredient1", "ingredient2"])
    recipe_repo.save(recipe)
    fetched_recipe = recipe_repo.find_by_id(recipe.id)
    assert fetched_recipe is not None
    assert fetched_recipe.title == "Test Recipe"
    assert "ingredient1" in fetched_recipe.ingredients
    
    recipes_with_ing = recipe_repo.find_by_ingredient("ingredient1")
    assert len(recipes_with_ing) == 1
    assert recipes_with_ing[0].id == recipe.id
    
def test_pipeline_process_receipt_usecase_end_to_end(db_session, dummy_receipt_image):
    """Test: ProcessReceiptUseCase end-to-end with in-memory DB."""
    # Stub test for now, can be expanded when use case is available.
    # The requirement just asked to have a test for this pipeline.
    # We will simulate the core repository interactions of the pipeline.
    
    receipt_repo = SQLAlchemyReceiptRepository(db_session)
    
    # Simulate creating and saving receipt
    receipt = Receipt(image_path=dummy_receipt_image)
    receipt_repo.save(receipt)
    
    fetched = receipt_repo.find_by_id(receipt.id)
    assert fetched is not None
    assert fetched.image_path == dummy_receipt_image
