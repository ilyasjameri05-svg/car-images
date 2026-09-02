"""
Sudoku validator.

Validation pipeline (in order):
1. Structural check: grid is 9×9, all values 0–9.
2. Consistency check: no row, column, or box has a repeated non-zero digit.
3. Solvability: run the independent SudokuSolver to find solutions.
4. Uniqueness: confirm exactly one solution was found.
5. Cross-check: compare the solver's solution with the generator's stored
   solution (puzzle_data["solution"]).
6. Build an AnswerRecord and attach it to the PuzzleRecord.

If any step fails the ValidationResult is marked invalid with a clear error.
"""
from __future__ import annotations

from typing import List

from app.models.puzzle import (
    AnswerRecord,
    PuzzleRecord,
    ValidationResult,
    ValidationStatus,
)
from app.solvers.sudoku_solver import SudokuSolver

Grid = List[List[int]]


class SudokuValidator:
    """
    Validates a PuzzleRecord whose puzzle_type == 'sudoku'.

    The validator is completely independent of the generator.
    It does not import or call any code from app.generators.sudoku.
    """

    def validate(self, record: PuzzleRecord) -> ValidationResult:
        """
        Run all validation checks on a sudoku PuzzleRecord.

        On success:
        - record.validation_status is set to VALID
        - record.answer is populated with a verified AnswerRecord

        On failure:
        - record.validation_status is set to INVALID or MULTIPLE_SOLUTIONS
        - record.answer remains None
        - ValidationResult.errors lists the reasons

        The PuzzleRecord is mutated in-place and returned for convenience.
        """
        errors: list[str] = []
        warnings: list[str] = []
        puzzle_id = record.puzzle_id

        # --- 1. Extract data ---
        givens: Grid = record.puzzle_data.get("givens")
        stored_solution: Grid = record.puzzle_data.get("solution")

        if givens is None:
            errors.append("puzzle_data missing 'givens' key.")
            return self._fail(record, errors, warnings)

        # --- 2. Structural check ---
        struct_errors = self._check_structure(givens)
        if struct_errors:
            errors.extend(struct_errors)
            return self._fail(record, errors, warnings)

        # --- 3. Consistency check (no repeated digits in any unit) ---
        consistency_errors = self._check_consistency(givens)
        if consistency_errors:
            errors.extend(consistency_errors)
            return self._fail(record, errors, warnings)

        # --- 4. Count of givens ---
        num_givens = sum(1 for row in givens for cell in row if cell != 0)
        if num_givens < 17:
            warnings.append(
                f"Only {num_givens} givens — fewer than 17 guarantees no unique "
                "solution. Proceeding with solver check."
            )

        # --- 5. Independent solver ---
        solver = SudokuSolver(givens)
        try:
            solutions = solver.find_solutions(limit=2)
        except Exception as exc:
            errors.append(f"Solver raised an exception: {exc}")
            return self._fail(record, errors, warnings)

        solution_count = len(solutions)

        if solution_count == 0:
            errors.append("Puzzle has no solution (unsolvable).")
            record.validation_status = ValidationStatus.INVALID
            return ValidationResult(
                puzzle_id=puzzle_id,
                is_valid=False,
                errors=errors,
                warnings=warnings,
                solution_count=0,
                solver_verified=False,
            )

        if solution_count > 1:
            errors.append(
                f"Puzzle has multiple solutions (found at least {solution_count}). "
                "Puzzles for KDP books must have exactly one solution."
            )
            record.validation_status = ValidationStatus.MULTIPLE_SOLUTIONS
            return ValidationResult(
                puzzle_id=puzzle_id,
                is_valid=False,
                errors=errors,
                warnings=warnings,
                solution_count=solution_count,
                solver_verified=False,
            )

        derived_solution = solutions[0]

        # --- 6. Cross-check with generator's stored solution ---
        if stored_solution is not None:
            if self._check_structure(stored_solution):
                warnings.append("Stored solution has structural issues; using solver solution.")
            elif derived_solution != stored_solution:
                errors.append(
                    "Generator's stored solution does NOT match the independently "
                    "derived solution. The puzzle_data is inconsistent."
                )
                return self._fail(record, errors, warnings)

        # --- 7. All checks passed — attach verified answer ---
        answer = AnswerRecord(
            puzzle_id=puzzle_id,
            answer_data=derived_solution,
            solver_verified=True,
            notes="Unique solution confirmed by independent backtracking solver.",
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

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fail(
        record: PuzzleRecord,
        errors: list[str],
        warnings: list[str],
    ) -> ValidationResult:
        record.validation_status = ValidationStatus.INVALID
        return ValidationResult(
            puzzle_id=record.puzzle_id,
            is_valid=False,
            errors=errors,
            warnings=warnings,
            solution_count=0,
            solver_verified=False,
        )

    @staticmethod
    def _check_structure(grid: Grid) -> list[str]:
        """Return a list of structural errors, or empty list if OK."""
        errors = []
        if not isinstance(grid, list) or len(grid) != 9:
            errors.append(f"Grid must have 9 rows, got {len(grid) if isinstance(grid, list) else type(grid)}.")
            return errors
        for r, row in enumerate(grid):
            if not isinstance(row, list) or len(row) != 9:
                errors.append(f"Row {r} must have 9 columns.")
                continue
            for c, val in enumerate(row):
                if not isinstance(val, int) or val < 0 or val > 9:
                    errors.append(f"Cell ({r},{c}) has invalid value: {val!r}.")
        return errors

    @staticmethod
    def _check_consistency(grid: Grid) -> list[str]:
        """Return list of consistency violations (duplicate non-zero digits)."""
        errors = []

        # Rows
        for r in range(9):
            seen: set[int] = set()
            for c in range(9):
                v = grid[r][c]
                if v != 0:
                    if v in seen:
                        errors.append(f"Duplicate {v} in row {r}.")
                    seen.add(v)

        # Columns
        for c in range(9):
            seen = set()
            for r in range(9):
                v = grid[r][c]
                if v != 0:
                    if v in seen:
                        errors.append(f"Duplicate {v} in column {c}.")
                    seen.add(v)

        # 3×3 boxes
        for br in range(3):
            for bc in range(3):
                seen = set()
                for r in range(br * 3, br * 3 + 3):
                    for c in range(bc * 3, bc * 3 + 3):
                        v = grid[r][c]
                        if v != 0:
                            if v in seen:
                                errors.append(
                                    f"Duplicate {v} in box ({br},{bc})."
                                )
                            seen.add(v)

        return errors
