"""
Picture Puzzle Validator.
"""
from __future__ import annotations

from app.models.puzzle import (
    AnswerRecord,
    PuzzleRecord,
    ValidationResult,
    ValidationStatus,
)
from app.validators.base import BasePuzzleValidator

class PicturePuzzleValidator(BasePuzzleValidator):
    def validate(self, record: PuzzleRecord) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        puzzle_id = record.puzzle_id
        d = record.puzzle_data

        for key in ("grid", "grid_rows", "grid_cols", "odd_row", "odd_col", "dominant", "odd_shape"):
            if key not in d:
                errors.append(f"Missing key: '{key}'")
        
        if errors:
            return self._fail(record, errors, warnings)

        grid = d["grid"]
        rows, cols = d["grid_rows"], d["grid_cols"]
        odd_r, odd_c = d["odd_row"], d["odd_col"]
        dominant = d["dominant"]
        odd_shape = d["odd_shape"]

        if len(grid) != rows:
            errors.append(f"Expected {rows} rows, got {len(grid)}.")
            return self._fail(record, errors, warnings)
        
        # Validate cells and independently find the odd cell
        found_odd_cells = []
        dominant_count = 0
        
        for r in range(rows):
            if len(grid[r]) != cols:
                errors.append(f"Row {r} expected {cols} cols, got {len(grid[r])}.")
                continue
            
            for c in range(cols):
                cell = grid[r][c]
                if cell != dominant:
                    found_odd_cells.append((r, c, cell))
                else:
                    dominant_count += 1

        if errors:
            return self._fail(record, errors, warnings)

        if len(found_odd_cells) != 1:
            errors.append(f"Expected exactly 1 odd cell, found {len(found_odd_cells)}.")
            return self._fail(record, errors, warnings)

        derived_odd_r, derived_odd_c, derived_odd_shape = found_odd_cells[0]
        
        if derived_odd_r != odd_r or derived_odd_c != odd_c:
            errors.append(f"Stored odd location ({odd_r}, {odd_c}) does not match derived location ({derived_odd_r}, {derived_odd_c}).")
            
        if derived_odd_shape != odd_shape:
            errors.append(f"Stored odd shape {odd_shape} does not match derived odd shape {derived_odd_shape}.")

        if dominant_count != rows * cols - 1:
            errors.append(f"Expected {rows*cols-1} dominant cells, found {dominant_count}.")

        if errors:
            return self._fail(record, errors, warnings)

        answer = AnswerRecord(
            puzzle_id=puzzle_id,
            answer_data={"odd_row": derived_odd_r, "odd_col": derived_odd_c, "odd_shape": derived_odd_shape},
            solver_verified=True,
            notes=f"Exactly one odd-shape cell confirmed at ({derived_odd_r},{derived_odd_c}) by scanning the grid.",
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
