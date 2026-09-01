"""
Tests for the page layout engine.
"""
import pytest
from backend.renderers.page_layout import calculate_layout, LayoutZone


class TestPageLayoutEngine:
    @pytest.mark.parametrize("page_size,orientation", [
        ("a4", "portrait"),
        ("a4", "landscape"),
        ("us_letter", "portrait"),
        ("us_letter", "landscape"),
        ("kdp_8_5x11", "portrait"),
        ("kdp_8_5x11", "landscape"),
        ("kdp_8x10", "portrait"),
        ("kdp_8x10", "landscape"),
    ])
    def test_all_page_size_combos(self, page_size, orientation):
        """All page size / orientation combinations should work."""
        layout = calculate_layout(page_size, orientation, 30, 30)
        assert layout.cell_size > 0
        assert layout.grid_zone.width > 0
        assert layout.grid_zone.height > 0

    @pytest.mark.parametrize("grid_size", [20, 30, 40, 50, 60])
    def test_all_grid_sizes(self, grid_size):
        layout = calculate_layout("kdp_8_5x11", "portrait", grid_size, grid_size)
        expected_w = layout.cell_size * grid_size
        assert abs(layout.grid_zone.width - expected_w) < 0.01

    def test_margins_respected(self):
        """Grid must be within safe margins."""
        layout = calculate_layout("kdp_8_5x11", "portrait", 30, 30)
        gz = layout.grid_zone
        assert gz.x >= layout.margin_inside - 1
        assert gz.right <= layout.page_width - layout.margin_outside + 1

    def test_color_key_below_grid(self):
        """Color key zone should be below the grid zone."""
        layout = calculate_layout("kdp_8_5x11", "portrait", 30, 30, color_count=10)
        assert layout.color_key_zone.y >= layout.grid_zone.bottom

    def test_unknown_page_size_fallback(self):
        """Unknown page size should fall back to kdp_8_5x11."""
        layout = calculate_layout("unknown_size", "portrait", 30, 30)
        assert layout.page_width > 0
