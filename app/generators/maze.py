"""
Maze puzzle generator using recursive backtracking (depth-first search).

Algorithm:
1. Create a grid of cells, each initially with all 4 walls intact.
2. Start at (0, 0), mark it visited.
3. While there are unvisited neighbours, pick one at random, remove the
   shared wall, and recurse.
4. Backtrack when no unvisited neighbours remain.

The result is a perfect maze (exactly one path between any two cells).

Wall representation per cell: {"N": bool, "S": bool, "E": bool, "W": bool}
  True  = wall exists (cannot pass)
  False = passage (wall has been removed)

Entry: top-left cell (0, 0), north wall opened
Exit:  bottom-right cell (rows-1, cols-1), south wall opened

puzzle_data keys:
  walls       — 2D list of wall dicts  (rows × cols)
  rows, cols  — int
  start       — [0, 0]
  end         — [rows-1, cols-1]
  solution    — list of [r, c] pairs (path from start to end, for answer key)
"""
from __future__ import annotations

import random
from typing import Optional

from app.generators.base import BasePuzzleGenerator
from app.models.book import BookSettings
from app.models.puzzle import PuzzleRecord, ValidationStatus

# Maze dimensions by difficulty (must be odd for clean rendering)
_MAZE_SIZES: dict[str, tuple[int, int]] = {
    "easy":   (11, 11),
    "medium": (15, 15),
    "hard":   (19, 19),
}

_INSTRUCTIONS: dict[str, str] = {
    "english": "Find the path from START (top-left) to FINISH (bottom-right) without crossing any walls.",
    "french":  "Trouvez le chemin du DÉPART (coin supérieur gauche) à l'ARRIVÉE (coin inférieur droit).",
    "spanish": "Encuentra el camino desde el INICIO (arriba-izquierda) hasta el FIN (abajo-derecha).",
    "arabic":  "ابحث عن المسار من البداية (أعلى اليسار) إلى النهاية (أسفل اليمين).",
}

# Opposite directions
_OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
# Neighbour offsets
_DELTA = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}

WallCell = dict[str, bool]  # {"N": bool, "S": bool, "E": bool, "W": bool}
WallGrid = list[list[WallCell]]


def _make_wall_grid(rows: int, cols: int) -> WallGrid:
    return [
        [{"N": True, "S": True, "E": True, "W": True} for _ in range(cols)]
        for _ in range(rows)
    ]


class MazeGenerator(BasePuzzleGenerator):
    def __init__(self, settings: BookSettings, difficulty: str = None, seed: Optional[int] = None) -> None:
        super().__init__(settings, difficulty=difficulty)
        self._seed = seed

    def generate(self) -> PuzzleRecord:
        rng = random.Random(self._seed)
        diff = self.difficulty
        rows, cols = _MAZE_SIZES.get(diff, (15, 15))

        walls = _make_wall_grid(rows, cols)
        visited = [[False] * cols for _ in range(rows)]

        # Recursive backtracking (iterative via explicit stack to avoid Python recursion limit)
        self._carve(walls, visited, 0, 0, rows, cols, rng)

        # Open the entry (north wall of top-left) and exit (south wall of bottom-right)
        walls[0][0]["N"] = False
        walls[rows - 1][cols - 1]["S"] = False

        # Solve with BFS to find the solution path (stored for answer key)
        solution = self._bfs_solve(walls, rows, cols)

        instructions = _INSTRUCTIONS.get(self.language, _INSTRUCTIONS["english"])

        return PuzzleRecord(
            puzzle_type="maze",
            difficulty=diff,
            language=self.language,
            title=f"Maze Challenge #{rng.randint(100, 999)}",
            instructions=instructions,
            puzzle_data={
                "walls":    walls,
                "rows":     rows,
                "cols":     cols,
                "start":    [0, 0],
                "end":      [rows - 1, cols - 1],
                "solution": [list(p) for p in solution],
            },
            validation_status=ValidationStatus.PENDING,
            seed=self._seed,
        )

    # ------------------------------------------------------------------
    # Maze carving (iterative DFS)
    # ------------------------------------------------------------------

    def _carve(
        self,
        walls: WallGrid,
        visited: list[list[bool]],
        sr: int,
        sc: int,
        rows: int,
        cols: int,
        rng: random.Random,
    ) -> None:
        stack = [(sr, sc)]
        visited[sr][sc] = True

        while stack:
            r, c = stack[-1]
            dirs = list(_DELTA.keys())
            rng.shuffle(dirs)

            moved = False
            for d in dirs:
                dr, dc = _DELTA[d]
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                    # Remove wall
                    walls[r][c][d] = False
                    walls[nr][nc][_OPPOSITE[d]] = False
                    visited[nr][nc] = True
                    stack.append((nr, nc))
                    moved = True
                    break

            if not moved:
                stack.pop()

    # ------------------------------------------------------------------
    # BFS solver (used only to store the solution path)
    # ------------------------------------------------------------------

    def _bfs_solve(
        self,
        walls: WallGrid,
        rows: int,
        cols: int,
    ) -> list[tuple[int, int]]:
        from collections import deque
        start = (0, 0)
        end   = (rows - 1, cols - 1)
        queue: deque[tuple[tuple[int, int], list]] = deque()
        queue.append((start, [start]))
        seen: set[tuple[int, int]] = {start}

        while queue:
            (r, c), path = queue.popleft()
            if (r, c) == end:
                return path
            for d, (dr, dc) in _DELTA.items():
                if not walls[r][c][d]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if (nr, nc) not in seen:
                            seen.add((nr, nc))
                            queue.append(((nr, nc), path + [(nr, nc)]))

        return []  # should never happen in a perfect maze
