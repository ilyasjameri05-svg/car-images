"""
Data models for individual puzzle records and answer records.

Every puzzle that enters the system must be represented as a PuzzleRecord.
The AnswerRecord stores the verified solution separately.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Puzzle status tracking
# ---------------------------------------------------------------------------

class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    MULTIPLE_SOLUTIONS = "multiple_solutions"


# ---------------------------------------------------------------------------
# Answer record — stored independently from the puzzle
# ---------------------------------------------------------------------------

class AnswerRecord(BaseModel):
    """
    The verified solution for a single puzzle.

    answer_data is puzzle-type-specific:
      - Sudoku: List[List[int]] — the fully solved 9x9 grid
      - Word search: Dict[str, List[Tuple[int,int]]] — word → coordinates
      - Maze: List[Tuple[int,int]] — path coordinates
    """
    puzzle_id: str
    answer_data: Any  # type-specific; validated by each puzzle validator
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    solver_verified: bool = Field(default=False)
    notes: str = Field(default="")


# ---------------------------------------------------------------------------
# Puzzle record — the central artefact for a single puzzle
# ---------------------------------------------------------------------------

class PuzzleRecord(BaseModel):
    """
    A complete, self-contained record for one generated puzzle.

    puzzle_data holds all information needed to reproduce the puzzle exactly:
      - Sudoku: {"givens": List[List[int]], "difficulty": str}
      - The puzzle_id is used for deduplication and linking to the answer key.
    """
    puzzle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    puzzle_type: str  # matches PuzzleType enum value
    difficulty: str   # matches Difficulty enum value
    language: str = Field(default="english")
    title: str = Field(default="")
    instructions: str = Field(default="")
    puzzle_data: Dict[str, Any] = Field(default_factory=dict)
    answer: Optional[AnswerRecord] = None
    validation_status: ValidationStatus = Field(default=ValidationStatus.PENDING)
    page_number: Optional[int] = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    seed: Optional[int] = None  # RNG seed for reproducibility

    @property
    def is_valid(self) -> bool:
        return self.validation_status == ValidationStatus.VALID

    @property
    def has_answer(self) -> bool:
        return self.answer is not None and self.answer.solver_verified


# ---------------------------------------------------------------------------
# Validation result returned by every validator
# ---------------------------------------------------------------------------

class ValidationResult(BaseModel):
    """Returned by a validator after checking a PuzzleRecord."""
    puzzle_id: str
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    solution_count: int = Field(default=0)  # 0 = unknown, 1 = unique, 2+ = ambiguous
    solver_verified: bool = Field(default=False)
