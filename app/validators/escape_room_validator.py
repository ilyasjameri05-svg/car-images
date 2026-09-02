"""
Escape Room Validator.
"""
from __future__ import annotations

from app.models.puzzle import (
    AnswerRecord,
    PuzzleRecord,
    ValidationResult,
    ValidationStatus,
)
from app.validators.base import BasePuzzleValidator
from app.data.problem_banks import ESCAPE_ROOM_PUZZLES

class EscapeRoomValidator(BasePuzzleValidator):
    def validate(self, record: PuzzleRecord) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        puzzle_id = record.puzzle_id
        d = record.puzzle_data

        for key in ("problem_id", "steps", "final_code"):
            if key not in d:
                errors.append(f"Missing key: '{key}'")
        
        if errors:
            return self._fail(record, errors, warnings)

        problem_id = d["problem_id"]
        
        # Verify against the problem bank
        bank_problem = next((p for p in ESCAPE_ROOM_PUZZLES if p["id"] == problem_id), None)
        
        if not bank_problem:
            errors.append(f"Problem ID '{problem_id}' not found in the curated problem bank.")
            return self._fail(record, errors, warnings)

        # Verify steps and final code match the bank
        if len(d["steps"]) != len(bank_problem["steps"]):
            errors.append(f"Expected {len(bank_problem['steps'])} steps, got {len(d['steps'])}.")
        else:
            for i, (gen_step, bank_step) in enumerate(zip(d["steps"], bank_problem["steps"])):
                if gen_step["clue"] != bank_step["clue"]:
                    errors.append(f"Step {i+1} clue does not match the bank.")
                if gen_step["answer"] != bank_step["answer"]:
                    errors.append(f"Step {i+1} answer does not match the bank.")
                    
        if d["final_code"] != bank_problem["final_code"]:
            errors.append("Stored final_code does not match the bank's final_code.")

        if errors:
            return self._fail(record, errors, warnings)

        answer = AnswerRecord(
            puzzle_id=puzzle_id,
            answer_data={
                "steps": d["steps"],
                "final_code": d["final_code"]
            },
            solver_verified=False,
            notes="Steps and final code are from a curated bank. Independent machine verification is unavailable for these riddles.",
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
