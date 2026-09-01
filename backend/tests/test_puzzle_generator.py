"""
Tests for the puzzle generator (orchestrator).
"""
import pytest
from PIL import Image
from backend.core.puzzle_generator import generate_puzzle, PuzzleData


class TestPuzzleGenerator:
    def test_basic_generation(self, sample_image):
        """Basic puzzle generation should work."""
        puzzle = generate_puzzle(sample_image, grid_width=20, grid_height=20,
                                 color_count=6, seed=42)
        assert isinstance(puzzle, PuzzleData)
        assert puzzle.grid_width == 20
        assert puzzle.grid_height == 20
        assert len(puzzle.cells) == 400
        assert len(puzzle.palette) == 6

    def test_deterministic_seed(self, sample_image):
        """Same inputs + same seed = same output."""
        p1 = generate_puzzle(sample_image, 20, 20, 8, seed=42)
        p2 = generate_puzzle(sample_image, 20, 20, 8, seed=42)

        assert len(p1.cells) == len(p2.cells)
        for c1, c2 in zip(p1.cells, p2.cells):
            assert c1["row"] == c2["row"]
            assert c1["col"] == c2["col"]
            assert c1["color_id"] == c2["color_id"]
            assert c1["color_hex"] == c2["color_hex"]

    def test_puzzle_answer_key_identity(self, sample_image):
        """Puzzle and answer key must use the SAME PuzzleData.

        The architecture guarantees this by generating PuzzleData once.
        This test verifies the data structure supports both renderers.
        """
        puzzle = generate_puzzle(sample_image, 30, 30, 10, seed=42)

        # Every cell has color_id (for puzzle renderer)
        for cell in puzzle.cells:
            assert "color_id" in cell, f"Cell at ({cell['row']},{cell['col']}) missing color_id"

        # Every cell has color_hex (for answer renderer)
        for cell in puzzle.cells:
            assert "color_hex" in cell, f"Cell at ({cell['row']},{cell['col']}) missing color_hex"

        # All palette entries exist
        palette_ids = {p.color_id for p in puzzle.palette}
        for cell in puzzle.cells:
            assert cell["color_id"] in palette_ids

    def test_to_dict(self, sample_image):
        """PuzzleData should serialize to dict properly."""
        puzzle = generate_puzzle(sample_image, 20, 20, 6, seed=42)
        d = puzzle.to_dict()

        assert "grid_width" in d
        assert "grid_height" in d
        assert "cells" in d
        assert "palette" in d
        assert d["grid_width"] == 20
        assert len(d["cells"]) == 400

    def test_portrait_image(self, portrait_image):
        """Should handle portrait images without distortion."""
        puzzle = generate_puzzle(portrait_image, 30, 30, 8)
        assert len(puzzle.cells) == 900

    def test_landscape_image(self, landscape_image):
        """Should handle landscape images without distortion."""
        puzzle = generate_puzzle(landscape_image, 30, 30, 8)
        assert len(puzzle.cells) == 900

    @pytest.mark.parametrize("grid_size", [20, 30, 40, 50])
    def test_various_grid_sizes(self, sample_image, grid_size):
        """Should work with all supported grid sizes."""
        puzzle = generate_puzzle(sample_image, grid_size, grid_size, 8)
        assert len(puzzle.cells) == grid_size * grid_size

    @pytest.mark.parametrize("color_count", [6, 8, 10, 12, 15, 20])
    def test_various_color_counts(self, sample_image, color_count):
        """Should work with all supported color counts."""
        puzzle = generate_puzzle(sample_image, 20, 20, color_count)
        assert len(puzzle.palette) == color_count

    def test_auto_color_count(self, sample_image):
        """Should resolve 'auto' color_count to an optimal palette."""
        puzzle = generate_puzzle(sample_image, 30, 30, color_count="auto", seed=42)
        assert len(puzzle.palette) in [6, 8, 10, 12, 15, 20]
        assert len(puzzle.cells) == 30 * 30
