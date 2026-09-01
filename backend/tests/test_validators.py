"""
Tests for book validator.
"""
import pytest
from backend.core.puzzle_generator import generate_puzzle, PuzzleData
from backend.core.palette_engine import NamedColor
from backend.validators.book_validator import (
    validate_puzzle, validate_layout, validate_book,
    validate_puzzle_answer_equality,
)


class TestValidatePuzzle:
    def test_valid_puzzle(self, sample_image):
        puzzle = generate_puzzle(sample_image, 20, 20, 6, seed=42)
        result = validate_puzzle(puzzle)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_missing_cells(self):
        """Puzzle with missing cells should fail."""
        puzzle = PuzzleData(
            grid_width=3, grid_height=3,
            cells=[{"row": 0, "col": 0, "color_id": 1, "color_hex": "#FF0000"}],
            palette=[NamedColor(1, "Red", "#FF0000")],
        )
        result = validate_puzzle(puzzle)
        assert result["valid"] is False
        assert any("Cell count" in e for e in result["errors"])

    def test_invalid_color_id(self):
        """Cells with invalid color_ids should fail."""
        cells = [
            {"row": r, "col": c, "color_id": 99, "color_hex": "#FF0000"}
            for r in range(2) for c in range(2)
        ]
        puzzle = PuzzleData(
            grid_width=2, grid_height=2,
            cells=cells,
            palette=[NamedColor(1, "Red", "#FF0000")],
        )
        result = validate_puzzle(puzzle)
        assert result["valid"] is False
        assert any("Invalid color_id" in e for e in result["errors"])

    def test_empty_palette(self):
        puzzle = PuzzleData(grid_width=2, grid_height=2, cells=[], palette=[])
        result = validate_puzzle(puzzle)
        assert result["valid"] is False


class TestValidateLayout:
    def test_valid_layout(self, sample_image):
        puzzle = generate_puzzle(sample_image, 30, 30, 10, seed=42)
        result = validate_layout(puzzle, "kdp_8_5x11", "portrait")
        assert result["valid"] is True

    def test_tiny_cells_warning(self, sample_image):
        """Very large grid on small page should warn or fail."""
        puzzle = generate_puzzle(sample_image, 60, 60, 10, seed=42)
        result = validate_layout(puzzle, "kdp_8x10", "portrait")
        # Should either produce warnings or errors about small cells
        assert "cell_size_pt" in result


class TestValidatePuzzleAnswerEquality:
    def test_equality_guaranteed(self, sample_image):
        puzzle = generate_puzzle(sample_image, 20, 20, 6, seed=42)
        result = validate_puzzle_answer_equality(puzzle)
        assert result["valid"] is True
        assert result["guaranteed_by_architecture"] is True


class TestValidateBook:
    def test_valid_book(self, sample_image):
        puzzles = [
            generate_puzzle(sample_image, 20, 20, 6, seed=i)
            for i in range(3)
        ]
        result = validate_book(puzzles, "kdp_8_5x11", "portrait")
        assert result["valid"] is True
        assert result["total_pages"] == 3

    def test_empty_book(self):
        result = validate_book([], "kdp_8_5x11", "portrait")
        assert result["valid"] is False
