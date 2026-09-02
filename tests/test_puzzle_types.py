"""
Tests for all remaining Phase 3 puzzle types:
  code_breaker, matching, pattern, critical_thinking,
  picture_puzzle, escape_room, logic_grid.
"""
from __future__ import annotations

import pytest

from app.models.book import BookSettings, Difficulty, PuzzleType
from app.models.puzzle import ValidationStatus
from app.validators.puzzle_validator import PuzzleValidator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _settings(puzzle_type: PuzzleType, difficulty: str = "medium") -> BookSettings:
    diff_map = {"easy": Difficulty.EASY, "medium": Difficulty.MEDIUM, "hard": Difficulty.HARD}
    return BookSettings(
        title="Phase 3 Test",
        author="Tester",
        puzzle_types=[puzzle_type],
        )


def _gen_validate(puzzle_type: PuzzleType, difficulty: str = "medium", seed: int = 42):
    settings = _settings(puzzle_type, difficulty)
    if puzzle_type == PuzzleType.CODE_BREAKER:
        from app.generators.code_breaker import CodeBreakerGenerator
        rec = CodeBreakerGenerator(settings, difficulty=difficulty, seed=seed).generate()
    elif puzzle_type == PuzzleType.MATCHING:
        from app.generators.matching import MatchingGenerator
        rec = MatchingGenerator(settings, difficulty=difficulty, seed=seed).generate()
    elif puzzle_type == PuzzleType.PATTERN:
        from app.generators.pattern import PatternGenerator
        rec = PatternGenerator(settings, difficulty=difficulty, seed=seed).generate()
    elif puzzle_type == PuzzleType.CRITICAL_THINKING:
        from app.generators.critical_thinking import CriticalThinkingGenerator
        rec = CriticalThinkingGenerator(settings, difficulty=difficulty, seed=seed).generate()
    elif puzzle_type == PuzzleType.PICTURE_PUZZLE:
        from app.generators.picture_puzzle import PicturePuzzleGenerator
        rec = PicturePuzzleGenerator(settings, difficulty=difficulty, seed=seed).generate()
    elif puzzle_type == PuzzleType.ESCAPE_ROOM:
        from app.generators.escape_room import EscapeRoomGenerator
        rec = EscapeRoomGenerator(settings, difficulty=difficulty, seed=seed).generate()
    elif puzzle_type == PuzzleType.LOGIC_GRID:
        from app.generators.logic_grid import LogicGridGenerator
        rec = LogicGridGenerator(settings, difficulty=difficulty, seed=seed).generate()
    else:
        raise ValueError(f"Unknown type: {puzzle_type}")
    result = PuzzleValidator.validate(rec)
    return rec, result


ALL_SIMPLE_TYPES = [
    PuzzleType.CODE_BREAKER,
    PuzzleType.MATCHING,
    PuzzleType.PATTERN,
    PuzzleType.CRITICAL_THINKING,
    PuzzleType.PICTURE_PUZZLE,
    PuzzleType.ESCAPE_ROOM,
    PuzzleType.LOGIC_GRID,
]


# ---------------------------------------------------------------------------
# Code Breaker
# ---------------------------------------------------------------------------

class TestCodeBreaker:

    def test_generates_encoded_text(self):
        from app.generators.code_breaker import CodeBreakerGenerator
        settings = _settings(PuzzleType.CODE_BREAKER)
        rec = CodeBreakerGenerator(settings, difficulty="medium", seed=1).generate()
        assert "encoded" in rec.puzzle_data
        assert len(rec.puzzle_data["encoded"]) > 0

    def test_decoded_and_encoded_different(self):
        from app.generators.code_breaker import CodeBreakerGenerator
        settings = _settings(PuzzleType.CODE_BREAKER)
        rec = CodeBreakerGenerator(settings, difficulty="medium", seed=2).generate()
        # Letters should differ (shift > 0)
        dec_letters = "".join(c for c in rec.puzzle_data["decoded"] if c.isalpha())
        enc_letters = "".join(c for c in rec.puzzle_data["encoded"] if c.isalpha())
        assert dec_letters != enc_letters

    def test_shift_in_valid_range(self):
        from app.generators.code_breaker import CodeBreakerGenerator
        settings = _settings(PuzzleType.CODE_BREAKER)
        for seed in range(5):
            rec = CodeBreakerGenerator(settings, difficulty="medium", seed=seed).generate()
            assert 1 <= rec.puzzle_data["shift"] <= 25

    def test_alphabet_table_has_26_entries(self):
        from app.generators.code_breaker import CodeBreakerGenerator
        settings = _settings(PuzzleType.CODE_BREAKER)
        rec = CodeBreakerGenerator(settings, difficulty="medium", seed=3).generate()
        assert len(rec.puzzle_data["alphabet_table"]) == 26

    def test_validates(self):
        rec, result = _gen_validate(PuzzleType.CODE_BREAKER)
        assert result.is_valid, result.errors

    def test_validation_status_valid(self):
        rec, result = _gen_validate(PuzzleType.CODE_BREAKER)
        assert rec.validation_status == ValidationStatus.VALID

    def test_reencoding_check_works(self):
        """If we corrupt the decoded text, validation must fail."""
        from app.generators.code_breaker import CodeBreakerGenerator
        from app.validators.code_breaker_validator import CodeBreakerValidator
        settings = _settings(PuzzleType.CODE_BREAKER)
        rec = CodeBreakerGenerator(settings, difficulty="medium", seed=5).generate()
        rec.puzzle_data["decoded"] = "WRONG TEXT"
        result = CodeBreakerValidator().validate(rec)
        assert not result.is_valid


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

class TestMatching:

    def test_left_and_right_same_length(self):
        from app.generators.matching import MatchingGenerator
        settings = _settings(PuzzleType.MATCHING)
        rec = MatchingGenerator(settings, difficulty="medium", seed=1).generate()
        d = rec.puzzle_data
        assert len(d["left_items"]) == len(d["right_items"])

    def test_correct_map_is_bijection(self):
        from app.generators.matching import MatchingGenerator
        settings = _settings(PuzzleType.MATCHING)
        rec = MatchingGenerator(settings, difficulty="medium", seed=2).generate()
        cmap = rec.puzzle_data["correct_map"]
        rights = list(cmap.values())
        assert len(rights) == len(set(rights)), "correct_map is not a bijection"

    def test_validates(self):
        rec, result = _gen_validate(PuzzleType.MATCHING)
        assert result.is_valid, result.errors

    def test_all_difficulties(self):
        for diff in ("easy", "medium", "hard"):
            rec, result = _gen_validate(PuzzleType.MATCHING, difficulty=diff)
            assert result.is_valid, f"Matching {diff} failed: {result.errors}"


# ---------------------------------------------------------------------------
# Pattern
# ---------------------------------------------------------------------------

class TestPattern:

    def test_generates_sequences(self):
        from app.generators.pattern import PatternGenerator
        settings = _settings(PuzzleType.PATTERN)
        rec = PatternGenerator(settings, difficulty="medium", seed=1).generate()
        assert "sequences" in rec.puzzle_data
        assert len(rec.puzzle_data["sequences"]) > 0

    def test_each_sequence_has_blanks(self):
        from app.generators.pattern import PatternGenerator
        settings = _settings(PuzzleType.PATTERN)
        rec = PatternGenerator(settings, difficulty="medium", seed=2).generate()
        for seq in rec.puzzle_data["sequences"]:
            assert "___" in seq["display"]

    def test_each_sequence_has_answers(self):
        from app.generators.pattern import PatternGenerator
        settings = _settings(PuzzleType.PATTERN)
        rec = PatternGenerator(settings, difficulty="medium", seed=3).generate()
        for seq in rec.puzzle_data["sequences"]:
            assert len(seq["answers"]) > 0

    def test_validates(self):
        rec, result = _gen_validate(PuzzleType.PATTERN)
        assert result.is_valid, result.errors

    def test_hard_has_fewer_sequences(self):
        easy_rec, _ = _gen_validate(PuzzleType.PATTERN, "easy")
        hard_rec, _ = _gen_validate(PuzzleType.PATTERN, "hard")
        assert easy_rec.puzzle_data["count"] >= hard_rec.puzzle_data["count"]


# ---------------------------------------------------------------------------
# Critical Thinking
# ---------------------------------------------------------------------------

class TestCriticalThinking:

    def test_has_question(self):
        from app.generators.critical_thinking import CriticalThinkingGenerator
        settings = _settings(PuzzleType.CRITICAL_THINKING)
        rec = CriticalThinkingGenerator(settings, difficulty="medium", seed=1).generate()
        assert rec.puzzle_data["question"]

    def test_has_answer(self):
        from app.generators.critical_thinking import CriticalThinkingGenerator
        settings = _settings(PuzzleType.CRITICAL_THINKING)
        rec = CriticalThinkingGenerator(settings, difficulty="medium", seed=2).generate()
        assert rec.puzzle_data["answer"]

    def test_validates(self):
        rec, result = _gen_validate(PuzzleType.CRITICAL_THINKING)
        assert result.is_valid, result.errors

    def test_all_difficulties(self):
        for diff in ("easy", "medium", "hard"):
            rec, result = _gen_validate(PuzzleType.CRITICAL_THINKING, difficulty=diff)
            assert result.is_valid, f"CriticalThinking {diff}: {result.errors}"


# ---------------------------------------------------------------------------
# Picture Puzzle
# ---------------------------------------------------------------------------

class TestPicturePuzzle:

    def test_grid_dimensions_match(self):
        from app.generators.picture_puzzle import PicturePuzzleGenerator
        settings = _settings(PuzzleType.PICTURE_PUZZLE)
        rec = PicturePuzzleGenerator(settings, difficulty="medium", seed=1).generate()
        d = rec.puzzle_data
        assert len(d["grid"]) == d["grid_rows"]
        assert len(d["grid"][0]) == d["grid_cols"]

    def test_exactly_one_odd_cell(self):
        from app.generators.picture_puzzle import PicturePuzzleGenerator
        settings = _settings(PuzzleType.PICTURE_PUZZLE)
        rec = PicturePuzzleGenerator(settings, difficulty="medium", seed=2).generate()
        d = rec.puzzle_data
        odd_count = sum(
            1 for r in d["grid"] for cell in r
            if cell == d["odd_shape"]
        )
        assert odd_count == 1

    def test_odd_shape_differs_from_dominant(self):
        from app.generators.picture_puzzle import PicturePuzzleGenerator
        settings = _settings(PuzzleType.PICTURE_PUZZLE)
        rec = PicturePuzzleGenerator(settings, difficulty="medium", seed=3).generate()
        assert rec.puzzle_data["odd_shape"] != rec.puzzle_data["dominant"]

    def test_validates(self):
        rec, result = _gen_validate(PuzzleType.PICTURE_PUZZLE)
        assert result.is_valid, result.errors

    def test_validates_detects_extra_odd_cell(self):
        """If we add a second odd cell, validation must fail."""
        from app.generators.picture_puzzle import PicturePuzzleGenerator
        from app.validators.picture_puzzle_validator import PicturePuzzleValidator
        settings = _settings(PuzzleType.PICTURE_PUZZLE)
        rec = PicturePuzzleGenerator(settings, difficulty="medium", seed=4).generate()
        d = rec.puzzle_data
        # Corrupt: place odd_shape in another cell
        odd_r = (d["odd_row"] + 1) % d["grid_rows"]
        rec.puzzle_data["grid"][odd_r][0] = d["odd_shape"]
        result = PicturePuzzleValidator().validate(rec)
        assert not result.is_valid


# ---------------------------------------------------------------------------
# Escape Room
# ---------------------------------------------------------------------------

class TestEscapeRoom:

    def test_has_steps(self):
        from app.generators.escape_room import EscapeRoomGenerator
        settings = _settings(PuzzleType.ESCAPE_ROOM)
        rec = EscapeRoomGenerator(settings, difficulty="medium", seed=1).generate()
        assert len(rec.puzzle_data["steps"]) > 0

    def test_each_step_has_clue_and_answer(self):
        from app.generators.escape_room import EscapeRoomGenerator
        settings = _settings(PuzzleType.ESCAPE_ROOM)
        rec = EscapeRoomGenerator(settings, difficulty="medium", seed=2).generate()
        for step in rec.puzzle_data["steps"]:
            assert "clue" in step and step["clue"]
            assert "answer" in step and step["answer"]

    def test_final_code_not_empty(self):
        from app.generators.escape_room import EscapeRoomGenerator
        settings = _settings(PuzzleType.ESCAPE_ROOM)
        rec = EscapeRoomGenerator(settings, difficulty="medium", seed=3).generate()
        assert rec.puzzle_data["final_code"]

    def test_validates(self):
        rec, result = _gen_validate(PuzzleType.ESCAPE_ROOM)
        assert result.is_valid, result.errors

    def test_answer_contains_final_code(self):
        rec, result = _gen_validate(PuzzleType.ESCAPE_ROOM)
        assert "final_code" in rec.answer.answer_data


# ---------------------------------------------------------------------------
# Logic Grid
# ---------------------------------------------------------------------------

class TestLogicGrid:

    def test_generates_clues(self):
        from app.generators.logic_grid import LogicGridGenerator
        settings = _settings(PuzzleType.LOGIC_GRID)
        rec = LogicGridGenerator(settings, difficulty="medium", seed=1).generate()
        assert len(rec.puzzle_data["clues"]) > 0

    def test_solution_is_complete(self):
        from app.generators.logic_grid import LogicGridGenerator
        settings = _settings(PuzzleType.LOGIC_GRID)
        rec = LogicGridGenerator(settings, difficulty="medium", seed=2).generate()
        solution = rec.puzzle_data["solution"]
        n = rec.puzzle_data["num_items"]
        assert len(solution) == n
        for person, assignments in solution.items():
            assert len(assignments) == len(rec.puzzle_data["other_cats"])

    def test_validates(self):
        rec, result = _gen_validate(PuzzleType.LOGIC_GRID)
        assert result.is_valid, result.errors

    def test_solver_derives_correct_solution(self):
        from app.generators.logic_grid import LogicGridGenerator
        from app.solvers.logic_solver import LogicSolver
        settings = _settings(PuzzleType.LOGIC_GRID)
        rec = LogicGridGenerator(settings, difficulty="medium", seed=3).generate()
        d = rec.puzzle_data
        people = d["items"][d["primary"]]
        solver = LogicSolver(people, d["items"], d["other_cats"], d["clues"])
        derived = solver.solve()
        assert derived == d["solution"]

    def test_all_difficulties(self):
        for diff in ("easy", "medium", "hard"):
            rec, result = _gen_validate(PuzzleType.LOGIC_GRID, difficulty=diff)
            assert result.is_valid, f"LogicGrid {diff}: {result.errors}"


# ---------------------------------------------------------------------------
# PuzzleValidator orchestrator
# ---------------------------------------------------------------------------

class TestPuzzleValidatorOrchestrator:

    def test_supported_types(self):
        types = PuzzleValidator.supported_types()
        assert "sudoku"            in types
        assert "word_search"       in types
        assert "maze"              in types
        assert "code_breaker"      in types
        assert "matching"          in types
        assert "pattern"           in types
        assert "critical_thinking" in types
        assert "picture_puzzle"    in types
        assert "escape_room"       in types
        assert "logic_grid"        in types

    def test_all_simple_types_validate_at_each_difficulty(self):
        """Every puzzle type must pass validation at every difficulty."""
        for pt in ALL_SIMPLE_TYPES:
            for diff in ("easy", "medium", "hard"):
                try:
                    rec, result = _gen_validate(pt, difficulty=diff, seed=42)
                    assert result.is_valid, (
                        f"{pt.value} ({diff}) failed validation: {result.errors}"
                    )
                    assert rec.validation_status == ValidationStatus.VALID
                    assert rec.answer is not None
                    if pt in (PuzzleType.CRITICAL_THINKING, PuzzleType.ESCAPE_ROOM):
                        assert rec.answer.solver_verified is False
                    else:
                        assert rec.answer.solver_verified is True
                except Exception as exc:
                    pytest.fail(f"{pt.value} ({diff}) raised {type(exc).__name__}: {exc}")
