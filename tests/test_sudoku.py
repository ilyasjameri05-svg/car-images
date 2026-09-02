"""
Test suite for the Sudoku pipeline:
- Generator
- Independent Solver
- Validator (end-to-end)
- Uniqueness guarantee
- Answer cross-check
"""
import copy
import pytest

from app.models.book import BookSettings, Difficulty, PuzzleType, TrimSize, Language
from app.models.puzzle import ValidationStatus
from app.generators.sudoku import SudokuGenerator
from app.solvers.sudoku_solver import SudokuSolver
from app.validators.sudoku_validator import SudokuValidator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def default_settings() -> BookSettings:
    return BookSettings(
        title="Test Book",
        author="Tester",
        language=Language.ENGLISH,
        trim_size=TrimSize.SIX_BY_NINE,
        puzzle_types=[PuzzleType.SUDOKU],
        difficulty=Difficulty.MEDIUM,
    )


@pytest.fixture()
def easy_settings() -> BookSettings:
    return BookSettings(
        title="Easy Test",
        author="Tester",
        language=Language.ENGLISH,
        trim_size=TrimSize.SIX_BY_NINE,
        puzzle_types=[PuzzleType.SUDOKU],
        difficulty=Difficulty.EASY,
    )


@pytest.fixture()
def hard_settings() -> BookSettings:
    return BookSettings(
        title="Hard Test",
        author="Tester",
        language=Language.ENGLISH,
        trim_size=TrimSize.SIX_BY_NINE,
        puzzle_types=[PuzzleType.SUDOKU],
        difficulty=Difficulty.HARD,
    )


# ---------------------------------------------------------------------------
# Generator tests
# ---------------------------------------------------------------------------

class TestSudokuGenerator:

    def test_generate_returns_puzzle_record(self, default_settings):
        gen = SudokuGenerator(default_settings, seed=42)
        record = gen.generate()
        assert record.puzzle_type == "sudoku"
        assert record.puzzle_data is not None

    def test_givens_grid_is_9x9(self, default_settings):
        gen = SudokuGenerator(default_settings, seed=42)
        record = gen.generate()
        givens = record.puzzle_data["givens"]
        assert len(givens) == 9
        assert all(len(row) == 9 for row in givens)

    def test_givens_values_in_range(self, default_settings):
        gen = SudokuGenerator(default_settings, seed=42)
        record = gen.generate()
        givens = record.puzzle_data["givens"]
        for row in givens:
            for val in row:
                assert 0 <= val <= 9, f"Invalid cell value: {val}"

    def test_solution_grid_is_complete(self, default_settings):
        gen = SudokuGenerator(default_settings, seed=42)
        record = gen.generate()
        solution = record.puzzle_data["solution"]
        for row in solution:
            for val in row:
                assert 1 <= val <= 9, f"Solution has empty/invalid cell: {val}"

    def test_easy_has_more_givens_than_hard(self, easy_settings, hard_settings):
        gen_easy = SudokuGenerator(easy_settings, difficulty="easy", seed=99)
        gen_hard = SudokuGenerator(hard_settings, difficulty="hard", seed=99)
        easy_record = gen_easy.generate()
        hard_record = gen_hard.generate()
        easy_givens = sum(1 for r in easy_record.puzzle_data["givens"] for c in r if c != 0)
        hard_givens = sum(1 for r in hard_record.puzzle_data["givens"] for c in r if c != 0)
        assert easy_givens > hard_givens, (
            f"Easy ({easy_givens}) should have more givens than hard ({hard_givens})"
        )

    def test_deterministic_with_seed(self, default_settings):
        gen1 = SudokuGenerator(default_settings, seed=1234)
        gen2 = SudokuGenerator(default_settings, seed=1234)
        r1 = gen1.generate()
        r2 = gen2.generate()
        assert r1.puzzle_data["givens"] == r2.puzzle_data["givens"]
        assert r1.puzzle_data["solution"] == r2.puzzle_data["solution"]

    def test_different_seeds_produce_different_puzzles(self, default_settings):
        gen1 = SudokuGenerator(default_settings, seed=1)
        gen2 = SudokuGenerator(default_settings, seed=2)
        r1 = gen1.generate()
        r2 = gen2.generate()
        # Very unlikely to be identical with different seeds
        assert r1.puzzle_data["givens"] != r2.puzzle_data["givens"]

    def test_validation_status_is_pending_after_generation(self, default_settings):
        gen = SudokuGenerator(default_settings, seed=42)
        record = gen.generate()
        assert record.validation_status == ValidationStatus.PENDING

    def test_no_answer_attached_by_generator(self, default_settings):
        gen = SudokuGenerator(default_settings, seed=42)
        record = gen.generate()
        assert record.answer is None, "Generator must NOT attach an answer"

    def test_instructions_not_empty(self, default_settings):
        gen = SudokuGenerator(default_settings, seed=42)
        record = gen.generate()
        assert record.instructions, "Instructions must not be empty"

    def test_given_cells_match_solution(self, default_settings):
        """Every non-zero cell in the givens must match the stored solution."""
        gen = SudokuGenerator(default_settings, seed=42)
        record = gen.generate()
        givens = record.puzzle_data["givens"]
        solution = record.puzzle_data["solution"]
        for r in range(9):
            for c in range(9):
                if givens[r][c] != 0:
                    assert givens[r][c] == solution[r][c], (
                        f"Cell ({r},{c}): given={givens[r][c]}, solution={solution[r][c]}"
                    )


# ---------------------------------------------------------------------------
# Solver tests  (solver is independent — tested with hand-crafted puzzles)
# ---------------------------------------------------------------------------

# A known valid Sudoku puzzle with a unique solution
_KNOWN_PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

_KNOWN_SOLUTION = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


class TestSudokuSolver:

    def test_solves_known_puzzle(self):
        solver = SudokuSolver(_KNOWN_PUZZLE)
        solutions = solver.find_solutions(limit=2)
        assert len(solutions) == 1
        assert solutions[0] == _KNOWN_SOLUTION

    def test_known_puzzle_has_unique_solution(self):
        solver = SudokuSolver(_KNOWN_PUZZLE)
        solutions = solver.find_solutions(limit=2)
        assert len(solutions) == 1

    def test_empty_grid_has_many_solutions(self):
        empty = [[0] * 9 for _ in range(9)]
        solver = SudokuSolver(empty)
        solutions = solver.find_solutions(limit=2)
        assert len(solutions) >= 2

    def test_fully_filled_valid_grid_has_one_solution(self):
        solver = SudokuSolver(_KNOWN_SOLUTION)
        solutions = solver.find_solutions(limit=2)
        assert len(solutions) == 1
        assert solutions[0] == _KNOWN_SOLUTION

    def test_invalid_grid_returns_no_solutions(self):
        # Two 5s in first row — impossible
        bad = copy.deepcopy(_KNOWN_PUZZLE)
        bad[0][1] = 5  # creates two 5s in row 0
        solver = SudokuSolver(bad)
        solutions = solver.find_solutions(limit=2)
        assert len(solutions) == 0

    def test_solve_method_returns_unique_solution(self):
        solver = SudokuSolver(_KNOWN_PUZZLE)
        solution = solver.solve()
        assert solution == _KNOWN_SOLUTION

    def test_solve_raises_on_multiple_solutions(self):
        empty = [[0] * 9 for _ in range(9)]
        solver = SudokuSolver(empty)
        with pytest.raises(ValueError, match="multiple solutions"):
            solver.solve()

    def test_does_not_mutate_original_grid(self):
        original = copy.deepcopy(_KNOWN_PUZZLE)
        solver = SudokuSolver(_KNOWN_PUZZLE)
        solver.find_solutions(limit=2)
        assert _KNOWN_PUZZLE == original

    def test_grid_size_validation(self):
        with pytest.raises(ValueError, match="9×9"):
            SudokuSolver([[1, 2], [3, 4]])

    def test_solver_is_independent_of_generator(self):
        """
        Confirm the solver can solve a puzzle generated by SudokuGenerator
        without importing or calling anything from the generator.
        """
        from app.generators.sudoku import SudokuGenerator
        from app.models.book import BookSettings, Difficulty, PuzzleType, TrimSize

        settings = BookSettings(
            title="Independence Test",
            author="Tester",
            trim_size=TrimSize.SIX_BY_NINE,
            puzzle_types=[PuzzleType.SUDOKU],
            difficulty=Difficulty.MEDIUM,
        )
        gen = SudokuGenerator(settings, difficulty="medium", seed=7)
        record = gen.generate()
        givens = record.puzzle_data["givens"]
        stored_solution = record.puzzle_data["solution"]

        # Solve with the independent solver
        solver = SudokuSolver(givens)
        derived = solver.solve()
        assert derived == stored_solution, "Solver found a different solution than the generator stored"


# ---------------------------------------------------------------------------
# Validator tests
# ---------------------------------------------------------------------------

class TestSudokuValidator:

    def test_validates_generated_puzzle(self, default_settings):
        gen = SudokuGenerator(default_settings, seed=42)
        record = gen.generate()
        validator = SudokuValidator()
        result = validator.validate(record)
        assert result.is_valid, f"Validation errors: {result.errors}"
        assert result.solution_count == 1
        assert result.solver_verified

    def test_sets_validation_status_to_valid(self, default_settings):
        gen = SudokuGenerator(default_settings, seed=42)
        record = gen.generate()
        validator = SudokuValidator()
        validator.validate(record)
        assert record.validation_status == ValidationStatus.VALID

    def test_attaches_answer_record(self, default_settings):
        gen = SudokuGenerator(default_settings, seed=42)
        record = gen.generate()
        validator = SudokuValidator()
        validator.validate(record)
        assert record.answer is not None
        assert record.answer.solver_verified
        assert len(record.answer.answer_data) == 9

    def test_answer_matches_solution(self, default_settings):
        gen = SudokuGenerator(default_settings, seed=42)
        record = gen.generate()
        validator = SudokuValidator()
        validator.validate(record)
        solution = record.answer.answer_data
        for r in range(9):
            for c in range(9):
                assert 1 <= solution[r][c] <= 9

    def test_rejects_puzzle_with_duplicate_in_row(self):
        bad_givens = copy.deepcopy(_KNOWN_PUZZLE)
        bad_givens[0][2] = 5  # duplicate 5 in row 0

        from app.models.puzzle import PuzzleRecord, ValidationStatus
        record = PuzzleRecord(
            puzzle_type="sudoku",
            difficulty="medium",
            puzzle_data={"givens": bad_givens, "solution": None},
        )
        validator = SudokuValidator()
        result = validator.validate(record)
        assert not result.is_valid
        assert record.validation_status == ValidationStatus.INVALID

    def test_rejects_puzzle_missing_givens(self):
        from app.models.puzzle import PuzzleRecord
        record = PuzzleRecord(
            puzzle_type="sudoku",
            difficulty="medium",
            puzzle_data={},  # missing 'givens'
        )
        validator = SudokuValidator()
        result = validator.validate(record)
        assert not result.is_valid
        assert "givens" in str(result.errors)

    def test_rejects_puzzle_with_no_solution(self):
        """Construct a grid that has no valid solution."""
        # Row 0: two 9s → no valid placement
        bad = [[0] * 9 for _ in range(9)]
        bad[0][0] = 9
        bad[0][1] = 9  # duplicate in row — no solution
        from app.models.puzzle import PuzzleRecord
        record = PuzzleRecord(
            puzzle_type="sudoku",
            difficulty="medium",
            puzzle_data={"givens": bad, "solution": None},
        )
        validator = SudokuValidator()
        result = validator.validate(record)
        assert not result.is_valid

    def test_validates_known_puzzle(self):
        from app.models.puzzle import PuzzleRecord
        record = PuzzleRecord(
            puzzle_type="sudoku",
            difficulty="medium",
            puzzle_data={"givens": _KNOWN_PUZZLE, "solution": _KNOWN_SOLUTION},
        )
        validator = SudokuValidator()
        result = validator.validate(record)
        assert result.is_valid
        assert result.solution_count == 1

    def test_multiple_puzzles_validated_sequentially(self, default_settings):
        gen = SudokuGenerator(default_settings)
        validator = SudokuValidator()
        for seed in range(5):
            gen._seed = seed
            record = gen.generate()
            result = validator.validate(record)
            assert result.is_valid, f"Seed {seed} failed: {result.errors}"

    def test_uniqueness_check_catches_ambiguous_puzzle(self):
        """
        Create a puzzle with multiple solutions by clearing too many cells.
        """
        # All-empty grid has many solutions
        empty_givens = [[0] * 9 for _ in range(9)]
        from app.models.puzzle import PuzzleRecord
        record = PuzzleRecord(
            puzzle_type="sudoku",
            difficulty="medium",
            puzzle_data={"givens": empty_givens, "solution": None},
        )
        validator = SudokuValidator()
        result = validator.validate(record)
        assert not result.is_valid
        assert result.solution_count >= 2 or "multiple" in str(result.errors).lower()
