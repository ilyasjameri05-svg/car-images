"""
Abstract base class for all puzzle generators.

Every puzzle type must subclass BasePuzzleGenerator and implement `generate()`.
The generate() method must return a PuzzleRecord with puzzle_data populated
and validation_status set to PENDING (never VALID — validation is performed
by the independent validator).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.book import BookSettings
from app.models.puzzle import PuzzleRecord


class BasePuzzleGenerator(ABC):
    """
    Interface every puzzle generator must implement.

    The generator is responsible ONLY for producing puzzle_data.
    It must NOT validate the puzzle — that is the validator's job.
    """

    def __init__(self, settings: BookSettings, difficulty: str = None) -> None:
        self.settings = settings
        self._difficulty = difficulty

    @abstractmethod
    def generate(self) -> PuzzleRecord:
        """
        Generate one puzzle and return a PuzzleRecord.

        The returned record must have:
        - puzzle_type set correctly
        - puzzle_data populated with all data needed to reproduce the puzzle
        - validation_status = ValidationStatus.PENDING
        - instructions set in the configured language
        - answer NOT set (the validator sets it after verification)
        """
        ...

    @property
    def difficulty(self) -> str:
        return self._difficulty or "medium"

    @property
    def language(self) -> str:
        return self.settings.language.value
