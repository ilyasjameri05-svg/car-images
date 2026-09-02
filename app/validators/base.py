"""
Base class for all puzzle validators.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.puzzle import PuzzleRecord, ValidationResult


class BasePuzzleValidator(ABC):
    """Interface every validator must implement."""

    @abstractmethod
    def validate(self, record: PuzzleRecord) -> ValidationResult:
        """Validate record, mutate validation_status and answer in-place, return result."""
        ...
