"""
Independent Word Search solver.

Given a filled grid and a list of words, scans the grid in all 8 directions
to find each word. Completely independent of the generator.

Usage
-----
solver = WordSearchSolver(grid, words)
found = solver.find_all()
# found: {word: [{"start": [r, c], "dir": [dr, dc]}]}
# A word absent from found was not located in the grid.
"""
from __future__ import annotations

from typing import List, Dict

Grid = List[List[str]]

DIRECTIONS = [
    (0,  1),
    (0, -1),
    (1,  0),
    (-1, 0),
    (1,  1),
    (1, -1),
    (-1, 1),
    (-1,-1),
]


class WordSearchSolver:
    """Independently scan a word-search grid and locate all target words."""

    def __init__(self, grid: Grid, words: List[str]) -> None:
        if not grid or not grid[0]:
            raise ValueError("Grid must be non-empty.")
        self.grid = grid
        self.words = [w.upper().strip() for w in words]
        self.rows = len(grid)
        self.cols = len(grid[0])

    def find_all(self) -> Dict[str, List[Dict]]:
        """
        Returns a dict mapping each word to a list of found positions.
        Each position: {"start": [r, c], "dir": [dr, dc]}
        An empty list means the word was not found.
        """
        results: Dict[str, List[Dict]] = {}
        for word in self.words:
            results[word] = self._find_word(word)
        return results

    def _find_word(self, word: str) -> List[Dict]:
        found = []
        for r in range(self.rows):
            for c in range(self.cols):
                for dr, dc in DIRECTIONS:
                    if self._matches(word, r, c, dr, dc):
                        found.append({"start": [r, c], "dir": [dr, dc]})
        return found

    def _matches(self, word: str, row: int, col: int, dr: int, dc: int) -> bool:
        for i, letter in enumerate(word):
            r, c = row + i * dr, col + i * dc
            if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                return False
            if self.grid[r][c].upper() != letter:
                return False
        return True
