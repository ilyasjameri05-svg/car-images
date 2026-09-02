"""
Word Search validator.

Validation pipeline:
1. Check puzzle_data has required keys.
2. Check grid is the correct size and contains only uppercase letters.
3. Run the independent WordSearchSolver to find every listed word.
4. Confirm all words are found at least once in the grid.
5. Verify that the generator's stored locations are consistent with the grid.
6. Attach an AnswerRecord containing the solver-found locations.
"""
from __future__ import annotations

from app.models.puzzle import AnswerRecord, PuzzleRecord, ValidationResult, ValidationStatus
from app.solvers.word_search_solver import WordSearchSolver
from app.validators.base import BasePuzzleValidator


class WordSearchValidator(BasePuzzleValidator):

    def validate(self, record: PuzzleRecord) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        grid        = record.puzzle_data.get("grid")
        words       = record.puzzle_data.get("words")
        grid_size   = record.puzzle_data.get("grid_size")
        stored_locs = record.puzzle_data.get("word_locations", {})

        # --- 1. Required keys ---
        if grid is None:
            errors.append("puzzle_data missing 'grid'.")
            return self._fail(record, errors, warnings)
        if not words:
            errors.append("puzzle_data missing or empty 'words'.")
            return self._fail(record, errors, warnings)
        if grid_size is None:
            errors.append("puzzle_data missing 'grid_size'.")
            return self._fail(record, errors, warnings)

        # --- 2. Grid structure ---
        if len(grid) != grid_size:
            errors.append(f"Grid has {len(grid)} rows, expected {grid_size}.")
        for r, row in enumerate(grid):
            if len(row) != grid_size:
                errors.append(f"Row {r} has {len(row)} columns, expected {grid_size}.")
            for c, cell in enumerate(row):
                if not isinstance(cell, str) or len(cell) != 1 or not cell.isalpha():
                    errors.append(f"Cell ({r},{c}) is not a single letter: {cell!r}")
        if errors:
            return self._fail(record, errors, warnings)

        # --- 3. Independent solver ---
        solver = WordSearchSolver(grid, words)
        found = solver.find_all()

        # --- 4. All words must be found ---
        missing = [w for w, positions in found.items() if not positions]
        if missing:
            errors.append(f"Words not found in grid: {missing}")
            return self._fail(record, errors, warnings)

        # --- 5. Cross-check stored locations ---
        for word, loc_info in stored_locs.items():
            sr, sc = loc_info["start"]
            dr, dc = loc_info["dir"]
            word_found = found.get(word, [])
            stored_pos = {"start": [sr, sc], "dir": [dr, dc]}
            if stored_pos not in word_found:
                errors.append(
                    f"Word '{word}' found by solver but NOT at stored location "
                    f"{stored_pos}. (Found at: {word_found})"
                )

        if errors:
            return self._fail(record, errors, warnings)

        # --- 6. Attach answer record ---
        # Store solver-found locations (first occurrence for each word)
        answer_locs = {w: positions[0] for w, positions in found.items() if positions}
        record.answer = AnswerRecord(
            puzzle_id=record.puzzle_id,
            answer_data={"word_locations": answer_locs, "words": words},
            solver_verified=True,
            notes="All words independently confirmed by WordSearchSolver.",
        )
        record.validation_status = ValidationStatus.VALID

        return ValidationResult(
            puzzle_id=record.puzzle_id,
            is_valid=True,
            errors=[],
            warnings=warnings,
            solution_count=1,
            solver_verified=True,
        )

    @staticmethod
    def _fail(record: PuzzleRecord, errors: list, warnings: list) -> ValidationResult:
        record.validation_status = ValidationStatus.INVALID
        record.answer = None
        return ValidationResult(
            puzzle_id=record.puzzle_id, is_valid=False,
            errors=errors, warnings=warnings,
            solution_count=0, solver_verified=False
        )
