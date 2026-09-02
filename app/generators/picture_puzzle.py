"""
Picture Puzzle generator.

Creates a grid of simple geometric shapes where exactly one cell contains
a shape that differs from the dominant shape. The solver must find the
'odd one out'.

Shapes are represented as strings:
  "circle", "square", "triangle", "diamond", "star", "cross"

Variants are:
  "filled_circle", "hollow_circle", etc.

puzzle_data keys:
  grid         — 2D list of shape strings (rows × cols)
  grid_rows    — int
  grid_cols    — int
  odd_row      — int (0-indexed row of odd cell)
  odd_col      — int (0-indexed col of odd cell)
  dominant     — shape string of the majority
  odd_shape    — shape string of the outlier
  pattern_type — "shape" | "variant"
"""
from __future__ import annotations

import random
from typing import Optional

from app.generators.base import BasePuzzleGenerator
from app.models.book import BookSettings
from app.models.puzzle import PuzzleRecord, ValidationStatus

# Shape pairs: (dominant, odd)
_SHAPE_CONTRASTS: list[tuple[str, str]] = [
    ("filled_circle",   "hollow_circle"),
    ("filled_square",   "hollow_square"),
    ("filled_triangle", "hollow_triangle"),
    ("filled_circle",   "filled_square"),
    ("filled_square",   "filled_triangle"),
    ("filled_triangle", "filled_circle"),
    ("star",            "cross"),
    ("cross",           "diamond"),
    ("diamond",         "star"),
    ("filled_circle",   "diamond"),
    ("hollow_square",   "filled_square"),
    ("filled_triangle", "star"),
]

# Grid sizes by difficulty
_GRID_SIZES: dict[str, tuple[int, int]] = {
    "easy":   (3, 3),
    "medium": (4, 4),
    "hard":   (5, 5),
}

_INSTRUCTIONS: dict[str, str] = {
    "english": "Find the ONE shape that is different from all the others and circle it.",
    "french":  "Trouvez la SEULE forme différente de toutes les autres et entourez-la.",
    "spanish": "Encuentra la ÚNICA forma diferente de todas las demás y enciérrala en un círculo.",
    "arabic":  "ابحث عن الشكل الواحد المختلف عن جميع الأشكال الأخرى وضع دائرة حوله.",
}


class PicturePuzzleGenerator(BasePuzzleGenerator):
    def __init__(self, settings: BookSettings, difficulty: str = None, seed: Optional[int] = None) -> None:
        super().__init__(settings, difficulty=difficulty)
        self._seed = seed

    def generate(self) -> PuzzleRecord:
        rng = random.Random(self._seed)
        diff = self.difficulty
        rows, cols = _GRID_SIZES.get(diff, (4, 4))

        dominant, odd_shape = rng.choice(_SHAPE_CONTRASTS)

        # Place the odd shape at a random cell
        odd_row = rng.randint(0, rows - 1)
        odd_col = rng.randint(0, cols - 1)

        grid = [
            [dominant for _ in range(cols)]
            for _ in range(rows)
        ]
        grid[odd_row][odd_col] = odd_shape

        instructions = _INSTRUCTIONS.get(self.language, _INSTRUCTIONS["english"])

        return PuzzleRecord(
            puzzle_type="picture_puzzle",
            difficulty=diff,
            language=self.language,
            title=f"Spot the Difference #{rng.randint(100, 999)}",
            instructions=instructions,
            puzzle_data={
                "grid":         grid,
                "grid_rows":    rows,
                "grid_cols":    cols,
                "odd_row":      odd_row,
                "odd_col":      odd_col,
                "dominant":     dominant,
                "odd_shape":    odd_shape,
            },
            validation_status=ValidationStatus.PENDING,
            seed=self._seed,
        )
