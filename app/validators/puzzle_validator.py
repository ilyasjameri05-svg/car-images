"""
Central puzzle validator orchestrator.

Routes any PuzzleRecord to the correct specialist validator based on puzzle_type.
This is the single entry point used by run.py and the PDF pipeline.

Usage
-----
from app.validators.puzzle_validator import PuzzleValidator

result = PuzzleValidator.validate(record)
if result.is_valid:
    # record.answer is now populated and solver_verified = True
    ...
"""
from __future__ import annotations

from app.models.puzzle import PuzzleRecord, ValidationResult
from app.validators.sudoku_validator import SudokuValidator
from app.validators.word_search_validator import WordSearchValidator
from app.validators.maze_validator import MazeValidator
from app.validators.logic_grid_validator import LogicGridValidator
from app.validators.code_breaker_validator import CodeBreakerValidator
from app.validators.matching_validator import MatchingValidator
from app.validators.pattern_validator import PatternValidator
from app.validators.critical_thinking_validator import CriticalThinkingValidator
from app.validators.picture_puzzle_validator import PicturePuzzleValidator
from app.validators.escape_room_validator import EscapeRoomValidator

_SUDOKU_VALIDATOR            = SudokuValidator()
_WORD_SEARCH_VALIDATOR       = WordSearchValidator()
_MAZE_VALIDATOR              = MazeValidator()
_LOGIC_GRID_VALIDATOR        = LogicGridValidator()
_CODE_BREAKER_VALIDATOR      = CodeBreakerValidator()
_MATCHING_VALIDATOR          = MatchingValidator()
_PATTERN_VALIDATOR           = PatternValidator()
_CRITICAL_THINKING_VALIDATOR = CriticalThinkingValidator()
_PICTURE_PUZZLE_VALIDATOR    = PicturePuzzleValidator()
_ESCAPE_ROOM_VALIDATOR       = EscapeRoomValidator()

# Map puzzle_type → validator instance
_VALIDATORS = {
    "sudoku":            _SUDOKU_VALIDATOR,
    "word_search":       _WORD_SEARCH_VALIDATOR,
    "maze":              _MAZE_VALIDATOR,
    "logic_grid":        _LOGIC_GRID_VALIDATOR,
    "code_breaker":      _CODE_BREAKER_VALIDATOR,
    "matching":          _MATCHING_VALIDATOR,
    "pattern":           _PATTERN_VALIDATOR,
    "critical_thinking": _CRITICAL_THINKING_VALIDATOR,
    "picture_puzzle":    _PICTURE_PUZZLE_VALIDATOR,
    "escape_room":       _ESCAPE_ROOM_VALIDATOR,
}


class PuzzleValidator:
    """Static dispatcher to the correct puzzle validator."""

    @staticmethod
    def validate(record: PuzzleRecord) -> ValidationResult:
        """
        Validate the given PuzzleRecord.

        Mutates record.validation_status and record.answer in-place.
        Returns a ValidationResult describing the outcome.
        """
        if record.puzzle_type not in _VALIDATORS:
            raise ValueError(f"No validator registered for puzzle type: {record.puzzle_type}")
        validator = _VALIDATORS[record.puzzle_type]
        return validator.validate(record)

    @staticmethod
    def supported_types() -> list[str]:
        return list(_VALIDATORS.keys())
