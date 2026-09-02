"""
Tests for Word Search: generator, solver, and validator.
"""
from __future__ import annotations

import pytest
import string

from app.models.book import BookSettings, Difficulty, PuzzleType
from app.models.puzzle import ValidationStatus
from app.generators.word_search import WordSearchGenerator
from app.solvers.word_search_solver import WordSearchSolver
from app.validators.word_search_validator import WordSearchValidator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_settings(**kwargs) -> BookSettings:
    diff_map = {"easy": Difficulty.EASY, "medium": Difficulty.MEDIUM, "hard": Difficulty.HARD}
    return BookSettings(
        title="Test Word Search",
        author="Tester",
        puzzle_types=[PuzzleType.WORD_SEARCH],
        )


def _generate_validated(difficulty: str = "medium", seed: int = 42) -> any:
    settings = _make_settings()
    gen = WordSearchGenerator(settings, difficulty=difficulty, seed=seed)
    rec = gen.generate()
    validator = WordSearchValidator()
    result = validator.validate(rec)
    return rec, result


# ---------------------------------------------------------------------------
# Generator tests
# ---------------------------------------------------------------------------

class TestWordSearchGenerator:

    def test_generates_puzzle_record(self):
        settings = _make_settings()
        rec = WordSearchGenerator(settings, difficulty="medium", seed=1).generate()
        assert rec.puzzle_type == "word_search"

    def test_grid_is_square(self):
        settings = _make_settings()
        rec = WordSearchGenerator(settings, difficulty="medium", seed=2).generate()
        size = rec.puzzle_data["grid_size"]
        assert len(rec.puzzle_data["grid"]) == size
        for row in rec.puzzle_data["grid"]:
            assert len(row) == size

    def test_grid_contains_only_uppercase_letters(self):
        settings = _make_settings()
        rec = WordSearchGenerator(settings, difficulty="medium", seed=3).generate()
        for row in rec.puzzle_data["grid"]:
            for cell in row:
                assert cell in string.ascii_uppercase, f"Non-letter cell: {cell!r}"

    def test_words_are_placed(self):
        settings = _make_settings()
        rec = WordSearchGenerator(settings, difficulty="medium", seed=4).generate()
        assert len(rec.puzzle_data["words"]) >= 1

    def test_word_locations_stored(self):
        settings = _make_settings()
        rec = WordSearchGenerator(settings, difficulty="medium", seed=5).generate()
        words = rec.puzzle_data["words"]
        locs  = rec.puzzle_data["word_locations"]
        for w in words:
            assert w in locs, f"No location stored for word {w!r}"

    def test_deterministic_with_seed(self):
        settings = _make_settings()
        rec1 = WordSearchGenerator(settings, difficulty="medium", seed=99).generate()
        rec2 = WordSearchGenerator(settings, difficulty="medium", seed=99).generate()
        assert rec1.puzzle_data["grid"] == rec2.puzzle_data["grid"]
        assert rec1.puzzle_data["words"] == rec2.puzzle_data["words"]

    def test_different_seeds_give_different_grids(self):
        settings = _make_settings()
        rec1 = WordSearchGenerator(settings, difficulty="medium", seed=10).generate()
        rec2 = WordSearchGenerator(settings, difficulty="medium", seed=11).generate()
        assert rec1.puzzle_data["grid"] != rec2.puzzle_data["grid"]

    def test_easy_has_smaller_grid(self):
        easy = WordSearchGenerator(_make_settings(), difficulty="easy", seed=1).generate()
        hard = WordSearchGenerator(_make_settings(), difficulty="hard", seed=1).generate()
        assert easy.puzzle_data["grid_size"] <= hard.puzzle_data["grid_size"]

    def test_validation_status_pending_before_validation(self):
        settings = _make_settings()
        rec = WordSearchGenerator(settings, difficulty="medium", seed=6).generate()
        assert rec.validation_status == ValidationStatus.PENDING

    def test_theme_is_set(self):
        settings = _make_settings()
        rec = WordSearchGenerator(settings, difficulty="medium", seed=7).generate()
        assert rec.puzzle_data["theme"]

    def test_with_explicit_theme(self):
        settings = _make_settings()
        rec = WordSearchGenerator(settings, seed=8, theme="animals").generate()
        assert rec.puzzle_data["theme"] == "animals"


# ---------------------------------------------------------------------------
# Solver tests
# ---------------------------------------------------------------------------

class TestWordSearchSolver:

    def test_finds_horizontal_word(self):
        grid = [list("ABCDEFG"), list("HIJKLMN")]
        # "ABC" is at row 0 from col 0 right
        solver = WordSearchSolver(grid, ["ABC"])
        found = solver.find_all()
        assert len(found["ABC"]) >= 1
        pos = found["ABC"][0]
        assert pos["start"] == [0, 0]
        assert pos["dir"] == [0, 1]

    def test_finds_vertical_word(self):
        grid = [
            ["A", "X"],
            ["B", "Y"],
            ["C", "Z"],
        ]
        solver = WordSearchSolver(grid, ["ABC"])
        found = solver.find_all()
        assert len(found["ABC"]) >= 1

    def test_finds_diagonal_word(self):
        grid = [
            ["A", "X", "X"],
            ["X", "B", "X"],
            ["X", "X", "C"],
        ]
        solver = WordSearchSolver(grid, ["ABC"])
        found = solver.find_all()
        assert len(found["ABC"]) >= 1

    def test_missing_word_has_empty_list(self):
        grid = [["A", "B"], ["C", "D"]]
        solver = WordSearchSolver(grid, ["XYZ"])
        found = solver.find_all()
        assert found["XYZ"] == []

    def test_empty_grid_raises(self):
        with pytest.raises(ValueError):
            WordSearchSolver([], ["ABC"])

    def test_independent_of_generator(self):
        """Solver shares no imports/state with WordSearchGenerator."""
        import inspect
        import app.solvers.word_search_solver as sm
        src = inspect.getsource(sm)
        assert "WordSearchGenerator" not in src
        assert "from app.generators" not in src

    def test_case_insensitive(self):
        grid = [["a", "b", "c"]]
        solver = WordSearchSolver(grid, ["ABC"])
        found = solver.find_all()
        assert len(found["ABC"]) >= 1

    def test_multiple_words(self):
        grid = [
            list("CATDOG"),
            list("XXXXXX"),
        ]
        solver = WordSearchSolver(grid, ["CAT", "DOG"])
        found = solver.find_all()
        assert len(found["CAT"]) >= 1
        assert len(found["DOG"]) >= 1

    def test_backward_word(self):
        grid = [list("GFEDCBA")]  # "ABCDEFG" backwards
        solver = WordSearchSolver(grid, ["ABCDEFG"])
        found = solver.find_all()
        # Should find it going left
        assert len(found["ABCDEFG"]) >= 1


# ---------------------------------------------------------------------------
# Validator tests
# ---------------------------------------------------------------------------

class TestWordSearchValidator:

    def test_validates_generated_puzzle(self):
        rec, result = _generate_validated(seed=10)
        assert result.is_valid, result.errors

    def test_sets_status_valid(self):
        rec, result = _generate_validated(seed=11)
        assert rec.validation_status == ValidationStatus.VALID

    def test_attaches_answer_record(self):
        rec, result = _generate_validated(seed=12)
        assert rec.answer is not None

    def test_answer_is_solver_verified(self):
        rec, result = _generate_validated(seed=13)
        assert rec.answer.solver_verified is True

    def test_word_locations_in_answer(self):
        rec, result = _generate_validated(seed=14)
        assert "word_locations" in rec.answer.answer_data

    def test_all_words_found(self):
        rec, result = _generate_validated(seed=15)
        words = rec.puzzle_data["words"]
        found_locs = rec.answer.answer_data["word_locations"]
        for w in words:
            assert w in found_locs, f"Word {w!r} not found in answer"

    def test_rejects_missing_grid(self):
        settings = _make_settings()
        rec = WordSearchGenerator(settings, difficulty="medium", seed=1).generate()
        del rec.puzzle_data["grid"]
        validator = WordSearchValidator()
        result = validator.validate(rec)
        assert not result.is_valid
        assert rec.validation_status == ValidationStatus.INVALID

    def test_rejects_missing_words(self):
        settings = _make_settings()
        rec = WordSearchGenerator(settings, difficulty="medium", seed=1).generate()
        rec.puzzle_data["words"] = []
        validator = WordSearchValidator()
        result = validator.validate(rec)
        assert not result.is_valid

    def test_validates_all_difficulties(self):
        for diff in ("easy", "medium", "hard"):
            rec, result = _generate_validated(difficulty=diff, seed=42)
            assert result.is_valid, f"Difficulty {diff!r} failed: {result.errors}"

    def test_words_in_grid_at_stored_locations(self):
        rec, result = _generate_validated(seed=20)
        grid = rec.puzzle_data["grid"]
        size = rec.puzzle_data["grid_size"]
        for word, loc_info in rec.puzzle_data["word_locations"].items():
            sr, sc = loc_info["start"]
            dr, dc = loc_info["dir"]
            extracted = ""
            for k in range(len(word)):
                r, c = sr + k*dr, sc + k*dc
                if 0 <= r < size and 0 <= c < size:
                    extracted += grid[r][c]
            assert extracted == word, f"Word {word!r} not at stored location"
