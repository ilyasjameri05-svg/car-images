"""
Tests for Maze: generator, solver, and validator.
"""
from __future__ import annotations

import pytest

from app.models.book import BookSettings, Difficulty, PuzzleType
from app.models.puzzle import ValidationStatus
from app.generators.maze import MazeGenerator
from app.solvers.maze_solver import MazeSolver
from app.validators.maze_validator import MazeValidator


def _make_settings(**kwargs) -> BookSettings:
    diff_map = {"easy": Difficulty.EASY, "medium": Difficulty.MEDIUM, "hard": Difficulty.HARD}
    return BookSettings(
        title="Test Maze",
        author="Tester",
        puzzle_types=[PuzzleType.MAZE],
        )


def _generate_validated(difficulty: str = "easy", seed: int = 42):
    settings = _make_settings()
    rec = MazeGenerator(settings, difficulty=difficulty, seed=seed).generate()
    validator = MazeValidator()
    result = validator.validate(rec)
    return rec, result


# ---------------------------------------------------------------------------
# Generator tests
# ---------------------------------------------------------------------------

class TestMazeGenerator:

    def test_generates_puzzle_record(self):
        settings = _make_settings()
        rec = MazeGenerator(settings, difficulty="medium", seed=1).generate()
        assert rec.puzzle_type == "maze"

    def test_wall_grid_dimensions(self):
        settings = _make_settings()
        rec = MazeGenerator(settings, difficulty="medium", seed=2).generate()
        d = rec.puzzle_data
        rows, cols = d["rows"], d["cols"]
        assert len(d["walls"]) == rows
        for row in d["walls"]:
            assert len(row) == cols

    def test_all_cells_have_four_walls(self):
        settings = _make_settings()
        rec = MazeGenerator(settings, difficulty="medium", seed=3).generate()
        for row in rec.puzzle_data["walls"]:
            for cell in row:
                assert set(cell.keys()) == {"N", "S", "E", "W"}
                for v in cell.values():
                    assert isinstance(v, bool)

    def test_start_and_end_are_set(self):
        settings = _make_settings()
        rec = MazeGenerator(settings, difficulty="medium", seed=4).generate()
        d = rec.puzzle_data
        assert d["start"] == [0, 0]
        rows, cols = d["rows"], d["cols"]
        assert d["end"] == [rows - 1, cols - 1]

    def test_solution_path_stored(self):
        settings = _make_settings()
        rec = MazeGenerator(settings, difficulty="medium", seed=5).generate()
        path = rec.puzzle_data["solution"]
        assert isinstance(path, list)
        assert len(path) >= 1

    def test_solution_starts_and_ends_correctly(self):
        settings = _make_settings()
        rec = MazeGenerator(settings, difficulty="medium", seed=6).generate()
        d = rec.puzzle_data
        path = d["solution"]
        assert path[0] == d["start"]
        assert path[-1] == d["end"]

    def test_deterministic_with_seed(self):
        settings = _make_settings()
        rec1 = MazeGenerator(settings, difficulty="medium", seed=7).generate()
        rec2 = MazeGenerator(settings, difficulty="medium", seed=7).generate()
        assert rec1.puzzle_data["walls"] == rec2.puzzle_data["walls"]

    def test_different_seeds_different_mazes(self):
        settings = _make_settings()
        rec1 = MazeGenerator(settings, difficulty="medium", seed=1).generate()
        rec2 = MazeGenerator(settings, difficulty="medium", seed=2).generate()
        assert rec1.puzzle_data["walls"] != rec2.puzzle_data["walls"]

    def test_hard_maze_is_larger(self):
        easy = MazeGenerator(_make_settings(), difficulty="easy", seed=1).generate()
        hard = MazeGenerator(_make_settings(), difficulty="hard", seed=1).generate()
        assert hard.puzzle_data["rows"] > easy.puzzle_data["rows"]

    def test_validation_status_pending_before_validation(self):
        settings = _make_settings()
        rec = MazeGenerator(settings, difficulty="medium", seed=8).generate()
        assert rec.validation_status == ValidationStatus.PENDING


# ---------------------------------------------------------------------------
# Solver tests
# ---------------------------------------------------------------------------

class TestMazeSolver:

    def _simple_2x2_maze(self):
        """2×2 maze: open passage from (0,0)→(0,1)→(1,1). All other walls closed."""
        walls = [
            [{"N": True,  "S": True, "E": False, "W": True},   # (0,0): open east
             {"N": True,  "S": False,"E": True,  "W": False}],  # (0,1): open south, open west
            [{"N": True,  "S": True, "E": True,  "W": True},   # (1,0): all walls
             {"N": False, "S": True, "E": True,  "W": True}],  # (1,1): open north (from (0,1))
        ]
        return walls

    def test_solves_simple_maze(self):
        walls = self._simple_2x2_maze()
        solver = MazeSolver(walls, 2, 2, [0, 0], [1, 1])
        path = solver.solve()
        assert path is not None
        assert len(path) > 0
        assert path[0] == [0, 0]
        assert path[-1] == [1, 1]

    def test_is_solvable_true(self):
        walls = self._simple_2x2_maze()
        solver = MazeSolver(walls, 2, 2, [0, 0], [1, 1])
        assert solver.is_solvable()

    def test_is_solvable_false(self):
        # Fully walled maze — no passages at all
        walls = [
            [{"N": True, "S": True, "E": True, "W": True},
             {"N": True, "S": True, "E": True, "W": True}],
            [{"N": True, "S": True, "E": True, "W": True},
             {"N": True, "S": True, "E": True, "W": True}],
        ]
        solver = MazeSolver(walls, 2, 2, [0, 0], [1, 1])
        assert not solver.is_solvable()

    def test_start_equals_end(self):
        walls = [[{"N": True, "S": True, "E": True, "W": True}]]
        solver = MazeSolver(walls, 1, 1, [0, 0], [0, 0])
        path = solver.solve()
        assert path == [[0, 0]]

    def test_invalid_dimensions_raise(self):
        with pytest.raises(ValueError):
            MazeSolver([], 0, 0, [0, 0], [0, 0])

    def test_wrong_grid_size_raises(self):
        walls = [[{"N": True, "S": True, "E": True, "W": True}]]
        with pytest.raises(ValueError):
            MazeSolver(walls, 2, 2, [0, 0], [1, 1])  # declared 2x2 but only 1x1

    def test_independent_of_generator(self):
        """Solver imports nothing from the generator module."""
        import inspect
        import app.solvers.maze_solver as sm
        src = inspect.getsource(sm)
        assert "MazeGenerator" not in src
        assert "from app.generators" not in src

    def test_solves_generated_maze(self):
        settings = _make_settings()
        rec = MazeGenerator(settings, difficulty="medium", seed=99).generate()
        d = rec.puzzle_data
        solver = MazeSolver(d["walls"], d["rows"], d["cols"], d["start"], d["end"])
        path = solver.solve()
        assert path is not None and len(path) > 0

    def test_path_length_positive(self):
        settings = _make_settings()
        rec = MazeGenerator(settings, difficulty="medium", seed=100).generate()
        d = rec.puzzle_data
        solver = MazeSolver(d["walls"], d["rows"], d["cols"], d["start"], d["end"])
        assert solver.path_length() > 0


# ---------------------------------------------------------------------------
# Validator tests
# ---------------------------------------------------------------------------

class TestMazeValidator:

    def test_validates_easy_maze(self):
        rec, result = _generate_validated("easy", seed=1)
        assert result.is_valid, result.errors

    def test_validates_medium_maze(self):
        rec, result = _generate_validated("medium", seed=2)
        assert result.is_valid, result.errors

    def test_validates_hard_maze(self):
        rec, result = _generate_validated("hard", seed=3)
        assert result.is_valid, result.errors

    def test_sets_status_valid(self):
        rec, result = _generate_validated(seed=4)
        assert rec.validation_status == ValidationStatus.VALID

    def test_attaches_answer_record(self):
        rec, result = _generate_validated(seed=5)
        assert rec.answer is not None

    def test_answer_is_solver_verified(self):
        rec, result = _generate_validated(seed=6)
        assert rec.answer.solver_verified is True

    def test_answer_path_starts_and_ends_correctly(self):
        rec, result = _generate_validated(seed=7)
        path = rec.answer.answer_data["path"]
        d    = rec.puzzle_data
        assert path[0] == list(d["start"])
        assert path[-1] == list(d["end"])

    def test_rejects_missing_walls(self):
        settings = _make_settings()
        rec = MazeGenerator(settings, difficulty="medium", seed=1).generate()
        del rec.puzzle_data["walls"]
        result = MazeValidator().validate(rec)
        assert not result.is_valid
        assert rec.validation_status == ValidationStatus.INVALID

    def test_rejects_wrong_dimensions(self):
        settings = _make_settings()
        rec = MazeGenerator(settings, difficulty="medium", seed=1).generate()
        rec.puzzle_data["rows"] = 99  # wrong
        result = MazeValidator().validate(rec)
        assert not result.is_valid

    def test_multiple_mazes_all_valid(self):
        for seed in range(5):
            rec, result = _generate_validated(seed=seed)
            assert result.is_valid, f"seed={seed} failed: {result.errors}"
