"""
Independent Maze solver using BFS.

Completely independent of the maze generator. Accepts the same wall
representation format but shares no code with the generator.

Usage
-----
solver = MazeSolver(walls, rows, cols, start, end)
path = solver.solve()
# path: list of [r, c] from start to end, or [] if no path exists.
"""
from __future__ import annotations

from collections import deque
from typing import List, Optional

_DELTA = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}


class MazeSolver:
    """
    BFS solver for grid mazes encoded as wall dictionaries.

    walls[r][c] is a dict {"N": bool, "S": bool, "E": bool, "W": bool}
    where True means the wall exists (passage blocked).
    """

    def __init__(
        self,
        walls: List[List[dict]],
        rows: int,
        cols: int,
        start: List[int],
        end: List[int],
    ) -> None:
        if rows <= 0 or cols <= 0:
            raise ValueError("Maze must have positive dimensions.")
        if len(walls) != rows or any(len(row) != cols for row in walls):
            raise ValueError(f"walls must be {rows}×{cols}.")
        self.walls = walls
        self.rows = rows
        self.cols = cols
        self.start = tuple(start)
        self.end   = tuple(end)

    def solve(self) -> List[List[int]]:
        """
        Return the shortest path from start to end as a list of [r, c] pairs.
        Returns an empty list if no path exists.
        """
        start = self.start
        end   = self.end

        if start == end:
            return [list(start)]

        queue: deque[tuple[tuple, list]] = deque()
        queue.append((start, [start]))
        seen: set[tuple] = {start}

        while queue:
            (r, c), path = queue.popleft()
            for direction, (dr, dc) in _DELTA.items():
                if self.walls[r][c][direction]:
                    continue  # wall present
                nr, nc = r + dr, c + dc
                if (nr, nc) in seen:
                    continue
                if nr < 0 or nr >= self.rows or nc < 0 or nc >= self.cols:
                    continue
                new_path = path + [(nr, nc)]
                if (nr, nc) == end:
                    return [list(p) for p in new_path]
                seen.add((nr, nc))
                queue.append(((nr, nc), new_path))

        return []  # no path found

    def is_solvable(self) -> bool:
        return len(self.solve()) > 0

    def path_length(self) -> int:
        return len(self.solve())
