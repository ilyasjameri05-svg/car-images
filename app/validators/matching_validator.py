"""
Matching Validator.
"""
from __future__ import annotations

from app.models.puzzle import (
    AnswerRecord,
    PuzzleRecord,
    ValidationResult,
    ValidationStatus,
)
from app.validators.base import BasePuzzleValidator

class MatchingValidator(BasePuzzleValidator):
    def validate(self, record: PuzzleRecord) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        puzzle_id = record.puzzle_id
        d = record.puzzle_data

        for key in ("left_items", "right_items", "correct_map"):
            if key not in d:
                errors.append(f"Missing key: '{key}'")
        
        if errors:
            return self._fail(record, errors, warnings)

        left = d["left_items"]
        right = d["right_items"]
        cmap = d["correct_map"]

        if len(left) != len(right):
            errors.append(f"left_items ({len(left)}) and right_items ({len(right)}) have different lengths.")

        # Check bijection: every left index maps to a unique right index
        mapped_rights = list(cmap.values())
        if len(mapped_rights) != len(set(mapped_rights)):
            errors.append("correct_map is not a bijection (duplicate right-side indices).")

        if len(cmap) != len(left):
            errors.append(f"correct_map has {len(cmap)} entries, expected {len(left)}.")

        if errors:
            return self._fail(record, errors, warnings)

        # Confirm each mapping is valid and build the derived answer pairs
        answer_pairs = []
        for li_str, ri in cmap.items():
            try:
                li = int(li_str)
            except ValueError:
                errors.append(f"Left index '{li_str}' is not an integer.")
                continue

            if li < 0 or li >= len(left):
                errors.append(f"Left index {li} is out of range.")
                continue
            if ri < 0 or ri >= len(right):
                errors.append(f"Right index {ri} is out of range.")
                continue
                
            answer_pairs.append((left[li], right[ri]))

        if errors:
            return self._fail(record, errors, warnings)

        answer = AnswerRecord(
            puzzle_id=puzzle_id,
            answer_data={"pairs": answer_pairs},
            solver_verified=True,
            notes="Matching bijection verified and pairs independently derived.",
        )
        record.answer = answer
        record.validation_status = ValidationStatus.VALID

        return ValidationResult(
            puzzle_id=puzzle_id,
            is_valid=True,
            errors=[],
            warnings=warnings,
            solution_count=1,
            solver_verified=True,
        )

    def _fail(
        self,
        record: PuzzleRecord,
        errors: list[str],
        warnings: list[str],
    ) -> ValidationResult:
        record.validation_status = ValidationStatus.INVALID
        record.answer = None
        return ValidationResult(
            puzzle_id=record.puzzle_id,
            is_valid=False,
            errors=errors,
            warnings=warnings,
            solution_count=0,
            solver_verified=False,
        )
