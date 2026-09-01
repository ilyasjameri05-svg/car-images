"""
Tests for grid generation.
"""
import pytest
from PIL import Image
from backend.core.color_quantizer import quantize_colors
from backend.core.grid_generator import generate_grid


class TestGridGenerator:
    def _make_grid(self, image, grid_size, num_colors=6):
        quantized, palette_rgb = quantize_colors(image, num_colors, seed=42)
        cells = generate_grid(quantized, grid_size, grid_size, palette_rgb)
        return cells, palette_rgb

    @pytest.mark.parametrize("grid_size", [20, 30, 40, 50, 60])
    def test_all_grid_sizes(self, sample_image, grid_size):
        """Should produce correct number of cells for all grid sizes."""
        cells, _ = self._make_grid(sample_image, grid_size)
        expected = grid_size * grid_size
        assert len(cells) == expected, f"Expected {expected} cells, got {len(cells)}"

    def test_no_missing_cells(self, sample_image):
        """Every position must be filled — no gaps."""
        grid_size = 20
        cells, _ = self._make_grid(sample_image, grid_size)

        positions = {(c["row"], c["col"]) for c in cells}
        for r in range(grid_size):
            for c in range(grid_size):
                assert (r, c) in positions, f"Missing cell at ({r},{c})"

    def test_no_duplicate_cells(self, sample_image):
        """No duplicate cell positions."""
        grid_size = 30
        cells, _ = self._make_grid(sample_image, grid_size)

        positions = [(c["row"], c["col"]) for c in cells]
        assert len(positions) == len(set(positions)), "Duplicate cell positions found"

    def test_valid_color_ids(self, sample_image):
        """All color_ids must be valid (1-based, within palette range)."""
        num_colors = 8
        cells, palette_rgb = self._make_grid(sample_image, 20, num_colors)

        valid_ids = set(range(1, num_colors + 1))
        for cell in cells:
            assert cell["color_id"] in valid_ids, (
                f"Invalid color_id {cell['color_id']} at ({cell['row']},{cell['col']})"
            )

    def test_cells_have_required_fields(self, sample_image):
        """Each cell must have row, col, color_id, color_hex."""
        cells, _ = self._make_grid(sample_image, 20)
        for cell in cells:
            assert "row" in cell
            assert "col" in cell
            assert "color_id" in cell
            assert "color_hex" in cell
            assert cell["color_hex"].startswith("#")
            assert len(cell["color_hex"]) == 7

    def test_cell_bounds(self, sample_image):
        """All cells must be within grid bounds."""
        grid_size = 30
        cells, _ = self._make_grid(sample_image, grid_size)

        for cell in cells:
            assert 0 <= cell["row"] < grid_size
            assert 0 <= cell["col"] < grid_size
