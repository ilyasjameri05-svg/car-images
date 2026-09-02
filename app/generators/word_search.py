"""
Word Search puzzle generator.

Algorithm:
1. Choose a grid size based on difficulty.
2. Select words from the themed word list.
3. Place each word in the grid in a random direction; retry if no valid
   position is found after MAX_TRIES attempts (word is skipped).
4. Fill remaining empty cells with random letters.
5. Store the grid, word list, and exact word locations for the validator.

8 directions supported: horizontal, vertical, 4 diagonals (both forward and
backward for each).

puzzle_data keys:
  grid            — 2D list of uppercase letters (rows × cols)
  words           — list of words to find (uppercased)
  word_locations  — {word: {"start": [r, c], "dir": [dr, dc]}}
  grid_size       — int (grid is always square)
  theme           — theme name
"""
from __future__ import annotations

import random
import string
from typing import Optional

from app.generators.base import BasePuzzleGenerator
from app.models.book import BookSettings
from app.models.puzzle import PuzzleRecord, ValidationStatus
from app.data.word_lists import get_words, get_random_theme

# Directions: (delta_row, delta_col)
DIRECTIONS = [
    (0,  1),   # right
    (0, -1),   # left
    (1,  0),   # down
    (-1, 0),   # up
    (1,  1),   # down-right
    (1, -1),   # down-left
    (-1, 1),   # up-right
    (-1,-1),   # up-left
]

_GRID_SIZES: dict[str, int] = {
    "easy":   12,
    "medium": 15,
    "hard":   15,
}

_MAX_PLACE_TRIES = 200

_INSTRUCTIONS: dict[str, str] = {
    "english": (
        "Find all the hidden words in the grid. Words may read in any direction: "
        "across, down, or diagonally. Circle each word as you find it."
    ),
    "french": (
        "Trouvez tous les mots cachés dans la grille. Les mots peuvent se lire dans "
        "toutes les directions. Entourez chaque mot trouvé."
    ),
    "spanish": (
        "Encuentra todas las palabras ocultas en la cuadrícula. Las palabras pueden "
        "leerse en cualquier dirección. Rodea cada palabra cuando la encuentres."
    ),
    "arabic": (
        "ابحث عن جميع الكلمات المخفية في الشبكة. يمكن قراءة الكلمات في أي اتجاه. "
        "ضع دائرة حول كل كلمة تجدها."
    ),
}

Grid = list[list[str]]


class WordSearchGenerator(BasePuzzleGenerator):
    def __init__(
        self,
        settings: BookSettings,
        difficulty: str = None,
        seed: Optional[int] = None,
        theme: Optional[str] = None,
    ) -> None:
        super().__init__(settings, difficulty=difficulty)
        self._seed = seed
        self._theme = theme

    def generate(self) -> PuzzleRecord:
        rng = random.Random(self._seed)
        diff = self.difficulty
        size = _GRID_SIZES.get(diff, 15)
        theme = self._theme or get_random_theme(rng)
        words = get_words(theme, diff, rng)

        # Initialise empty grid
        grid: Grid = [[" "] * size for _ in range(size)]
        placed_words: list[str] = []
        word_locations: dict[str, dict] = {}

        for word in words:
            if len(word) > size:
                continue
            placed = self._place_word(grid, word, size, rng)
            if placed:
                start, direction = placed
                placed_words.append(word)
                word_locations[word] = {"start": list(start), "dir": list(direction)}

        # Fill empty cells with random uppercase letters
        for r in range(size):
            for c in range(size):
                if grid[r][c] == " ":
                    grid[r][c] = rng.choice(string.ascii_uppercase)

        instructions = _INSTRUCTIONS.get(self.language, _INSTRUCTIONS["english"])

        return PuzzleRecord(
            puzzle_type="word_search",
            difficulty=diff,
            language=self.language,
            title=f"Word Search: {theme.replace('_', ' ').title()} #{rng.randint(100, 999)}",
            instructions=instructions,
            puzzle_data={
                "grid":           grid,
                "words":          placed_words,
                "word_locations": word_locations,
                "grid_size":      size,
                "theme":          theme,
            },
            validation_status=ValidationStatus.PENDING,
            seed=self._seed,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _can_place(grid: Grid, word: str, row: int, col: int,
                   dr: int, dc: int, size: int) -> bool:
        for i, letter in enumerate(word):
            r, c = row + i * dr, col + i * dc
            if r < 0 or r >= size or c < 0 or c >= size:
                return False
            cell = grid[r][c]
            if cell != " " and cell != letter:
                return False
        return True

    @staticmethod
    def _do_place(grid: Grid, word: str, row: int, col: int,
                  dr: int, dc: int) -> None:
        for i, letter in enumerate(word):
            grid[row + i * dr][col + i * dc] = letter

    def _place_word(
        self,
        grid: Grid,
        word: str,
        size: int,
        rng: random.Random,
    ) -> Optional[tuple[tuple[int, int], tuple[int, int]]]:
        """Try to place `word` in the grid. Returns (start, direction) or None."""
        directions = list(DIRECTIONS)
        rng.shuffle(directions)

        positions = [(r, c) for r in range(size) for c in range(size)]
        rng.shuffle(positions)

        for dr, dc in directions:
            for row, col in positions:
                if self._can_place(grid, word, row, col, dr, dc, size):
                    self._do_place(grid, word, row, col, dr, dc)
                    return (row, col), (dr, dc)

        return None  # word could not be placed
