"""
Maze validator.

Validation pipeline:
1. Check puzzle_data has required keys.
2. Check wall grid dimensions.
3. Run the independent MazeSolver to confirm a path exists.
4. Verify the stored solution path is valid (each step follows a passage).
5. Confirm solver's path connects the same start/end as stored.
6. Attach AnswerRecord with the independently derived solution path.
"""
from __future__ import annotations

from app.models.puzzle import AnswerRecord, PuzzleRecord, ValidationResult, ValidationStatus
from app.solvers.maze_solver import MazeSolver
from app.validators.base import BasePuzzleValidator


class MazeValidator(BasePuzzleValidator):

    def validate(self, record: PuzzleRecord) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        walls    = record.puzzle_data.get("walls")
        rows     = record.puzzle_data.get("rows")
        cols     = record.puzzle_data.get("cols")
        start    = record.puzzle_data.get("start")
        end      = record.puzzle_data.get("end")
        stored_solution = record.puzzle_data.get("solution", [])

        # --- 1. Required keys ---
        for key, val in [("walls", walls), ("rows", rows), ("cols", cols),
                         ("start", start), ("end", end)]:
            if val is None:
                errors.append(f"puzzle_data missing '{key}'.")
        if errors:
            return self._fail(record, errors, warnings)

        # --- 2. Dimensions ---
        if len(walls) != rows:
            errors.append(f"walls has {len(walls)} rows, expected {rows}.")
        else:
            for r, row in enumerate(walls):
                if len(row) != cols:
                    errors.append(f"walls row {r} has {len(row)} cols, expected {cols}.")
                    break
        if errors:
            return self._fail(record, errors, warnings)

        # --- 3. Independent solver ---
        try:
            solver = MazeSolver(walls, rows, cols, start, end)
            path = solver.solve()
        except Exception as exc:
            errors.append(f"MazeSolver raised: {exc}")
            return self._fail(record, errors, warnings)

        if not path:
            errors.append("MazeSolver found no path from start to end — maze is not solvable.")
            return self._fail(record, errors, warnings)

        # --- 4. Validate stored path cells are reachable ---
        if stored_solution:
            stored_path = [tuple(p) for p in stored_solution]
            
            # Check adjacency and wall crossings for stored path
            if stored_path[0] != tuple(start):
                errors.append(f"Stored path starts at {stored_path[0]}, expected {start}.")
            if stored_path[-1] != tuple(end):
                errors.append(f"Stored path ends at {stored_path[-1]}, expected {end}.")
            
            for i in range(len(stored_path) - 1):
                r1, c1 = stored_path[i]
                r2, c2 = stored_path[i+1]
                
                # Check adjacency
                if abs(r1 - r2) + abs(c1 - c2) != 1:
                    errors.append(f"Stored path step {i} to {i+1} is not adjacent: ({r1},{c1}) to ({r2},{c2}).")
                    break
                    
                # Check bounds
                if not (0 <= r1 < rows and 0 <= c1 < cols) or not (0 <= r2 < rows and 0 <= c2 < cols):
                    errors.append(f"Stored path step out of bounds.")
                    break
                    
                # Check wall crossing
                valid = False
                for direction, (dr, dc) in {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}.items():
                    if dr == r2 - r1 and dc == c2 - c1:
                        if walls[r1][c1].get(direction):
                            break # Wall present
                        valid = True
                        break
                
                if not valid:
                    errors.append(f"Stored path crossed a wall or made illegal move from ({r1},{c1}) to ({r2},{c2}).")
                    break

            derived_path = [tuple(p) for p in path]
            if not errors and stored_path != derived_path:
                warnings.append(
                    "Generator's stored solution path differs from the independently "
                    "derived BFS path (both are valid — BFS gives shortest path)."
                )

        if errors:
            return self._fail(record, errors, warnings)

        # --- 5. Confirm path starts and ends correctly ---
        if list(path[0]) != list(start):
            errors.append(f"Solver path starts at {path[0]}, expected {start}.")
        if list(path[-1]) != list(end):
            errors.append(f"Solver path ends at {path[-1]}, expected {end}.")
        if errors:
            return self._fail(record, errors, warnings)

        # --- 6. Attach answer ---
        record.answer = AnswerRecord(
            puzzle_id=record.puzzle_id,
            answer_data={"path": path, "path_length": len(path)},
            solver_verified=True,
            notes="Path confirmed by independent BFS MazeSolver.",
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
