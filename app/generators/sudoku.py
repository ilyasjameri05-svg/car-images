"""
Sudoku puzzle generator.

Algorithm:
1. Build a fully solved 9×9 Sudoku grid using a randomised backtracking fill.
2. Remove cells one-by-one (in random order) while verifying, after each
   removal, that the puzzle still has exactly one solution.
3. Stop removing cells when the target number of givens is reached for the
   selected difficulty level.

This approach guarantees:
- The starting grid is a valid completed Sudoku.
- The puzzle has exactly one solution (checked after every removal).
- The generator is entirely independent from the solver/validator.

The generator does NOT call the external SudokuSolver.  That solver is used
only by the SudokuValidator (an independent component) to confirm the result
produced here.
"""
from __future__ import annotations

import copy
import random
from typing import List, Optional

from app.generators.base import BasePuzzleGenerator
from app.models.book import BookSettings, Difficulty
from app.models.puzzle import PuzzleRecord, ValidationStatus


# Number of givens (clues) by difficulty.
# These thresholds are drawn from published Sudoku research.
_GIVENS_BY_DIFFICULTY: dict[str, int] = {
    Difficulty.EASY.value:   46,
    Difficulty.MEDIUM.value: 35,
    Difficulty.HARD.value:   28,
    Difficulty.EXPERT.value: 24,
}

# Instructions text per language
_INSTRUCTIONS: dict[str, str] = {
    "english": (
        "Fill in the grid so that every row, every column, and every 3×3 box "
        "contains the digits 1–9 exactly once."
    ),
    "french": (
        "Remplissez la grille de façon que chaque ligne, colonne et carré 3×3 "
        "contienne les chiffres de 1 à 9 une seule fois."
    ),
    "spanish": (
        "Rellena la cuadrícula de modo que cada fila, columna y cuadro 3×3 "
        "contenga los dígitos del 1 al 9 exactamente una vez."
    ),
    "arabic": (
        "املأ الشبكة بحيث تحتوي كل صف وعمود ومربع 3×3 على الأرقام من 1 إلى 9 "
        "مرة واحدة فقط."
    ),
}

Grid = List[List[int]]  # 9×9, 0 = empty


class _InternalSolver:
    """
    Minimal backtracking solver used ONLY inside the generator to verify
    uniqueness during puzzle construction.

    This is a private implementation detail of the generator.
    The external SudokuSolver (in solvers/) is a completely separate class.
    """

    def __init__(self, grid: Grid) -> None:
        self.grid: Grid = copy.deepcopy(grid)
        self.solutions_found: int = 0

    def _is_valid(self, row: int, col: int, num: int) -> bool:
        # Row check
        if num in self.grid[row]:
            return False
        # Column check
        if any(self.grid[r][col] == num for r in range(9)):
            return False
        # Box check
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if self.grid[r][c] == num:
                    return False
        return True

    def _next_empty(self) -> Optional[tuple[int, int]]:
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    return r, c
        return None

    def count_solutions(self, limit: int = 2) -> int:
        """Count solutions, stopping once `limit` is reached (efficiency)."""
        self.solutions_found = 0
        self._count(limit)
        return self.solutions_found

    def _count(self, limit: int) -> None:
        if self.solutions_found >= limit:
            return
        cell = self._next_empty()
        if cell is None:
            self.solutions_found += 1
            return
        r, c = cell
        for num in range(1, 10):
            if self._is_valid(r, c, num):
                self.grid[r][c] = num
                self._count(limit)
                self.grid[r][c] = 0
                if self.solutions_found >= limit:
                    return


class SudokuGenerator(BasePuzzleGenerator):
    """Generates valid Sudoku puzzles with a guaranteed unique solution."""

    def __init__(self, settings: BookSettings, difficulty: str = None, seed: Optional[int] = None) -> None:
        super().__init__(settings, difficulty=difficulty)
        self._seed = seed

    def generate(self) -> PuzzleRecord:
        rng = random.Random(self._seed)

        # Step 1: Generate a fully solved grid
        solved = self._fill_grid(rng)

        # Step 2: Remove cells to reach the target number of givens
        target_givens = _GIVENS_BY_DIFFICULTY.get(self.difficulty, 35)
        puzzle_grid = self._create_puzzle(solved, target_givens, rng)

        # Count actual givens
        actual_givens = sum(1 for row in puzzle_grid for cell in row if cell != 0)

        instructions = _INSTRUCTIONS.get(self.language, _INSTRUCTIONS["english"])

        return PuzzleRecord(
            puzzle_type="sudoku",
            difficulty=self.difficulty,
            language=self.language,
            title=f"Sudoku #{rng.randint(1000, 9999)}",
            instructions=instructions,
            puzzle_data={
                "givens": puzzle_grid,          # 9×9 grid with 0s for empty
                "solution": solved,             # fully solved grid (used by validator)
                "num_givens": actual_givens,
                "difficulty": self.difficulty,
            },
            validation_status=ValidationStatus.PENDING,
            seed=self._seed,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fill_grid(self, rng: random.Random) -> Grid:
        """Return a fully solved 9×9 grid using randomised backtracking."""
        grid: Grid = [[0] * 9 for _ in range(9)]
        self._solve_fill(grid, rng)
        return grid

    def _is_valid_placement(self, grid: Grid, row: int, col: int, num: int) -> bool:
        if num in grid[row]:
            return False
        if any(grid[r][col] == num for r in range(9)):
            return False
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if grid[r][c] == num:
                    return False
        return True

    def _solve_fill(self, grid: Grid, rng: random.Random) -> bool:
        """Fill grid cells in order using shuffled digits for randomness."""
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    nums = list(range(1, 10))
                    rng.shuffle(nums)
                    for num in nums:
                        if self._is_valid_placement(grid, r, c, num):
                            grid[r][c] = num
                            if self._solve_fill(grid, rng):
                                return True
                            grid[r][c] = 0
                    return False
        return True

    def _create_puzzle(
        self, solved: Grid, target_givens: int, rng: random.Random
    ) -> Grid:
        """
        Remove cells from the solved grid while maintaining a unique solution.
        Returns a grid with exactly `target_givens` filled cells (or as close
        as possible while preserving uniqueness).
        """
        puzzle = copy.deepcopy(solved)
        current_givens = 81

        # Build a shuffled list of all 81 positions
        positions = [(r, c) for r in range(9) for c in range(9)]
        rng.shuffle(positions)

        for r, c in positions:
            if current_givens <= target_givens:
                break
            backup = puzzle[r][c]
            puzzle[r][c] = 0

            # Verify uniqueness after removal
            solver = _InternalSolver(puzzle)
            count = solver.count_solutions(limit=2)

            if count == 1:
                current_givens -= 1
            else:
                # Restoring is required: removing this cell breaks uniqueness
                puzzle[r][c] = backup

        return puzzle
