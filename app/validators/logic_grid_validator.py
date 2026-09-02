"""
Logic Grid Validator.
"""
from __future__ import annotations

from app.models.puzzle import (
    AnswerRecord,
    PuzzleRecord,
    ValidationResult,
    ValidationStatus,
)
from app.solvers.logic_solver import LogicSolver
from app.validators.base import BasePuzzleValidator

class LogicGridValidator(BasePuzzleValidator):
    def validate(self, record: PuzzleRecord) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        puzzle_id = record.puzzle_id
        d = record.puzzle_data

        for key in ("primary", "items", "other_cats", "clues", "solution"):
            if key not in d:
                errors.append(f"Missing key: '{key}'")
        
        if errors:
            return self._fail(record, errors, warnings)
            
        people = d["items"][d["primary"]]

        solver = LogicSolver(
            people=people,
            items_by_cat=d["items"],
            other_cats=d["other_cats"],
            clues=d["clues"]
        )
        
        solutions = solver.find_all_solutions()
        
        if len(solutions) == 0:
            errors.append("Puzzle has no solution (unsolvable) or contradictory clues.")
            return self._fail(record, errors, warnings)
        
        if len(solutions) > 1:
            errors.append("Puzzle has multiple solutions (not unique).")
            record.validation_status = ValidationStatus.MULTIPLE_SOLUTIONS
            record.answer = None
            return ValidationResult(
                puzzle_id=puzzle_id,
                is_valid=False,
                errors=errors,
                warnings=warnings,
                solution_count=len(solutions),
                solver_verified=False,
            )

        derived_solution = solutions[0]
        
        # Check against generator solution if provided
        stored_solution = d.get("solution")
        if stored_solution:
            if derived_solution != stored_solution:
                errors.append("Generator's stored solution does NOT match the independently derived solution.")
                return self._fail(record, errors, warnings)

        answer = AnswerRecord(
            puzzle_id=puzzle_id,
            answer_data=derived_solution,
            solver_verified=True,
            notes="Unique solution confirmed by independent logic solver.",
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
