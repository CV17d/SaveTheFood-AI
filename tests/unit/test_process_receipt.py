"""Unit tests for ProcessReceiptUseCase — State Pattern transitions."""

from __future__ import annotations

import pytest

from src.domain.entities.receipt import Receipt, ReceiptState, InvalidStateTransitionError


class TestReceiptStatePattern:
    """Tests for the Receipt State Pattern lifecycle."""

    def test_initial_state_is_uploaded(self) -> None:
        receipt = Receipt(image_path="/test.jpg")
        assert receipt.state == ReceiptState.UPLOADED

    def test_uploaded_to_processing(self) -> None:
        receipt = Receipt(image_path="/test.jpg")
        receipt.process()
        assert receipt.state == ReceiptState.PROCESSING

    def test_processing_to_parsed(self) -> None:
        receipt = Receipt(image_path="/test.jpg")
        receipt.process()
        receipt.mark_parsed()
        assert receipt.state == ReceiptState.PARSED

    def test_parsed_to_completed(self) -> None:
        receipt = Receipt(image_path="/test.jpg")
        receipt.process()
        receipt.mark_parsed()
        receipt.complete()
        assert receipt.state == ReceiptState.COMPLETED

    def test_invalid_transition_raises(self) -> None:
        receipt = Receipt(image_path="/test.jpg")
        with pytest.raises(InvalidStateTransitionError):
            receipt.complete()  # Cannot go UPLOADED → COMPLETED

    def test_processing_to_failed(self) -> None:
        receipt = Receipt(image_path="/test.jpg")
        receipt.process()
        receipt.mark_failed("OCR engine crashed")
        assert receipt.state == ReceiptState.FAILED
        assert receipt.failure_reason == "OCR engine crashed"

    def test_failed_allows_retry(self) -> None:
        receipt = Receipt(image_path="/test.jpg")
        receipt.process()
        receipt.mark_failed("Timeout")
        receipt.process()  # Retry from FAILED
        assert receipt.state == ReceiptState.PROCESSING
