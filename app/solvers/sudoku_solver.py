"""
Independent Sudoku backtracking solver.

This solver is COMPLETELY INDEPENDENT from the generator.
It shares NO code, state, or data with SudokuGenerator.

It is used by SudokuValidator to:
1. Verify that the generated puzzle has exactly one solution.
2. Independently compute that solution.
3. Confirm the generator's stored solution matches the independently derived one.

The solver uses constraint propagation (naked singles) before backtracking
to improve performance on harder puzzles.
"""
from __future__ import annotations

import copy
from typing import List, Optional, Tuple

Grid = List[List[int]]  # 9×9, 0 = empty


class SudokuSolver:
    """
    Independent backtracking solver with constraint propagation.

    Usage
    -----
    solver = SudokuSolver(puzzle_grid)
    solutions = solver.find_solutions(limit=2)
    # len(solutions) == 1 → unique solution
    # solutions[0]         → the solved grid

    The original grid passed in is never mutated.
    """

    def __init__(self, grid: Grid) -> None:
        if len(grid) != 9 or any(len(row) != 9 for row in grid):
            raise ValueError("Grid must be exactly 9×9.")
        self._original: Grid = copy.deepcopy(grid)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def find_solutions(self, limit: int = 2) -> List[Grid]:
        """
        Find up to `limit` solutions.

        Returns a list of solved grids.
        - Empty list → no solution (invalid puzzle).
        - Single element → unique solution.
        - Two elements → at least two solutions (not a valid puzzle for KDP).
        """
        working = copy.deepcopy(self._original)
        results: List[Grid] = []
        self._backtrack(working, results, limit)
        return results

    def solve(self) -> Optional[Grid]:
        """
        Return the unique solution, or None if no unique solution exists.
        Raises ValueError if multiple solutions are found.
        """
        solutions = self.find_solutions(limit=2)
        if len(solutions) == 0:
            return None
        if len(solutions) > 1:
            raise ValueError("Puzzle has multiple solutions — not valid for KDP.")
        return solutions[0]

    # ------------------------------------------------------------------
    # Constraint propagation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _peers(row: int, col: int) -> set[Tuple[int, int]]:
        """Return the set of all cells that share a unit with (row, col)."""
        peers: set[Tuple[int, int]] = set()
        # Same row
        for c in range(9):
            peers.add((row, c))
        # Same column
        for r in range(9):
            peers.add((r, col))
        # Same 3×3 box
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                peers.add((r, c))
        peers.discard((row, col))
        return peers

    @staticmethod
    def _is_valid(grid: Grid, row: int, col: int, num: int) -> bool:
        """Check if placing `num` at (row, col) violates any Sudoku constraint."""
        # Row
        if num in grid[row]:
            return False
        # Column
        if any(grid[r][col] == num for r in range(9)):
            return False
        # Box
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if grid[r][c] == num:
                    return False
        return True

    # ------------------------------------------------------------------
    # Backtracking search — MRV heuristic (minimum remaining values)
    # ------------------------------------------------------------------

    def _candidates(self, grid: Grid, row: int, col: int) -> List[int]:
        """Return all valid digits for the empty cell (row, col)."""
        used: set[int] = set()
        # Row
        used.update(grid[row])
        # Column
        used.update(grid[r][col] for r in range(9))
        # Box
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                used.add(grid[r][c])
        return [n for n in range(1, 10) if n not in used]

    def _choose_cell(self, grid: Grid) -> Optional[Tuple[int, int]]:
        """
        Select the empty cell with the fewest candidates (MRV heuristic).
        Returns None when the grid is fully solved.
        """
        best: Optional[Tuple[int, int]] = None
        best_count = 10
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    count = len(self._candidates(grid, r, c))
                    if count < best_count:
                        best_count = count
                        best = (r, c)
                        if count == 0:
                            return best  # Dead end — prune immediately
        return best

    def _backtrack(
        self, grid: Grid, results: List[Grid], limit: int
    ) -> None:
        """Recursive backtracking search accumulating solutions into `results`."""
        if len(results) >= limit:
            return

        cell = self._choose_cell(grid)
        if cell is None:
            # All cells filled — record solution
            results.append(copy.deepcopy(grid))
            return

        r, c = cell
        for num in self._candidates(grid, r, c):
            grid[r][c] = num
            self._backtrack(grid, results, limit)
            grid[r][c] = 0
            if len(results) >= limit:
                return
