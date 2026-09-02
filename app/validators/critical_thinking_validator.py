"""
Critical Thinking Validator.
"""
from __future__ import annotations

from app.models.puzzle import (
    AnswerRecord,
    PuzzleRecord,
    ValidationResult,
    ValidationStatus,
)
from app.validators.base import BasePuzzleValidator
from app.data.problem_banks import CRITICAL_THINKING_PROBLEMS

class CriticalThinkingValidator(BasePuzzleValidator):
    def validate(self, record: PuzzleRecord) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        puzzle_id = record.puzzle_id
        d = record.puzzle_data

        for key in ("problem_id", "question", "answer"):
            if key not in d or not d[key]:
                errors.append(f"Missing or empty: '{key}'")
        
        if errors:
            return self._fail(record, errors, warnings)

        problem_id = d["problem_id"]
        
        # Verify against the problem bank
        bank_problem = next((p for p in CRITICAL_THINKING_PROBLEMS if p["id"] == problem_id), None)
        
        if not bank_problem:
            errors.append(f"Problem ID '{problem_id}' not found in the curated problem bank.")
            return self._fail(record, errors, warnings)

        if bank_problem["question"] != d["question"]:
            errors.append("Stored question does not match the question in the problem bank.")
            
        if bank_problem["answer"] != d["answer"]:
            errors.append("Stored answer does not match the answer in the problem bank.")

        if errors:
            return self._fail(record, errors, warnings)

        # Critical thinking problems are language-dependent/non-deterministic logic problems
        # that we cannot independently solve with a python solver. We explicitly document this.
        answer = AnswerRecord(
            puzzle_id=puzzle_id,
            answer_data={"answer": d["answer"], "explanation": d.get("explanation", "")},
            solver_verified=False,  # Explicitly false per requirements
            notes="Answer is from a curated bank. Independent machine verification is unavailable for this non-deterministic logic problem.",
        )
        record.answer = answer
        record.validation_status = ValidationStatus.VALID

        return ValidationResult(
            puzzle_id=puzzle_id,
            is_valid=True,
            errors=[],
            warnings=warnings,
            solution_count=1,
            solver_verified=False,
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
