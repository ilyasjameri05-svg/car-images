"""
Tests for the layout engine and page dimension catalog.
"""
import pytest

from app.models.book import (
    BookSettings, Difficulty, Language, Orientation,
    PuzzleType, TrimSize
)
from app.models.layout import POINTS_PER_INCH
from app.layouts.dimensions import get_page_dimensions, list_standard_sizes
from app.layouts.page_layout import compute_page_layout


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def base_settings() -> BookSettings:
    return BookSettings(
        title="Layout Test",
        author="Tester",
        language=Language.ENGLISH,
        trim_size=TrimSize.SIX_BY_NINE,
        puzzle_types=[PuzzleType.SUDOKU],
        difficulty=Difficulty.MEDIUM,
    )


# ---------------------------------------------------------------------------
# PageDimensions tests
# ---------------------------------------------------------------------------

class TestPageDimensions:

    def test_6x9_dimensions(self, base_settings):
        dims = get_page_dimensions(base_settings)
        assert abs(dims.trim_width_in - 6.0) < 0.001
        assert abs(dims.trim_height_in - 9.0) < 0.001

    def test_8x10_dimensions(self, base_settings):
        base_settings = base_settings.model_copy(update={"trim_size": TrimSize.EIGHT_BY_TEN})
        dims = get_page_dimensions(base_settings)
        assert abs(dims.trim_width_in - 8.0) < 0.001
        assert abs(dims.trim_height_in - 10.0) < 0.001

    def test_8_5x11_dimensions(self, base_settings):
        base_settings = base_settings.model_copy(update={"trim_size": TrimSize.EIGHT_HALF_BY_ELEVEN})
        dims = get_page_dimensions(base_settings)
        assert abs(dims.trim_width_in - 8.5) < 0.001
        assert abs(dims.trim_height_in - 11.0) < 0.001

    def test_landscape_swaps_width_height(self, base_settings):
        portrait = base_settings.model_copy(update={"orientation": Orientation.PORTRAIT})
        landscape = base_settings.model_copy(update={"orientation": Orientation.LANDSCAPE})
        d_p = get_page_dimensions(portrait)
        d_l = get_page_dimensions(landscape)
        assert abs(d_p.trim_width_in - d_l.trim_height_in) < 0.001
        assert abs(d_p.trim_height_in - d_l.trim_width_in) < 0.001

    def test_bleed_increases_full_page_size(self, base_settings):
        no_bleed = base_settings.model_copy(update={"bleed": False})
        with_bleed = base_settings.model_copy(
            update={"bleed": True, "bleed_amount_in": 0.125}
        )
        d_no = get_page_dimensions(no_bleed)
        d_bl = get_page_dimensions(with_bleed)
        # Full page must be larger by 2 × bleed on each axis
        assert abs(d_bl.width - d_no.width - 2 * 0.125 * POINTS_PER_INCH) < 0.001
        assert abs(d_bl.height - d_no.height - 2 * 0.125 * POINTS_PER_INCH) < 0.001
        # Trim size must remain the same
        assert abs(d_bl.trim_width - d_no.trim_width) < 0.001

    def test_custom_dimensions(self):
        settings = BookSettings(
            title="Custom",
            author="Tester",
            trim_size=TrimSize.CUSTOM,
            custom_width_in=7.0,
            custom_height_in=10.0,
            puzzle_types=[PuzzleType.SUDOKU],
        )
        dims = get_page_dimensions(settings)
        assert abs(dims.trim_width_in - 7.0) < 0.001
        assert abs(dims.trim_height_in - 10.0) < 0.001

    def test_custom_requires_both_dimensions(self):
        with pytest.raises(ValueError):
            BookSettings(
                title="Bad Custom",
                author="Tester",
                trim_size=TrimSize.CUSTOM,
                puzzle_types=[PuzzleType.SUDOKU],
                # missing custom_width_in and custom_height_in
            )

    def test_points_conversion(self, base_settings):
        dims = get_page_dimensions(base_settings)
        assert abs(dims.width - dims.trim_width_in * POINTS_PER_INCH) < 0.001

    def test_list_standard_sizes_returns_all(self):
        sizes = list_standard_sizes()
        assert len(sizes) == 7  # 7 standard sizes defined
        ids = [s["id"] for s in sizes]
        assert "6x9" in ids
        assert "8x10" in ids
        assert "8.5x11" in ids


# ---------------------------------------------------------------------------
# PageLayout tests
# ---------------------------------------------------------------------------

class TestPageLayout:

    def test_layout_safe_area_positive(self, base_settings):
        dims = get_page_dimensions(base_settings)
        layout = compute_page_layout(base_settings, page_number=1, dims=dims)
        assert layout.safe_area_width > 0
        assert layout.safe_area_height > 0

    def test_layout_content_area_positive(self, base_settings):
        dims = get_page_dimensions(base_settings)
        layout = compute_page_layout(base_settings, page_number=1, dims=dims)
        assert layout.content_width > 0
        assert layout.content_height > 0

    def test_safe_area_within_page(self, base_settings):
        dims = get_page_dimensions(base_settings)
        layout = compute_page_layout(base_settings, page_number=1, dims=dims)
        # Safe area must not overflow the page
        assert layout.safe_area_x >= 0
        assert layout.safe_area_y >= 0
        assert layout.safe_area_x + layout.safe_area_width <= dims.trim_width + 0.001
        assert layout.safe_area_y + layout.safe_area_height <= dims.trim_height + 0.001

    def test_content_within_safe_area(self, base_settings):
        dims = get_page_dimensions(base_settings)
        layout = compute_page_layout(base_settings, page_number=1, dims=dims)
        assert layout.content_x >= layout.safe_area_x - 0.001
        assert layout.content_y >= layout.safe_area_y - 0.001
        assert (layout.content_x + layout.content_width
                <= layout.safe_area_x + layout.safe_area_width + 0.001)
        assert (layout.content_y + layout.content_height
                <= layout.safe_area_y + layout.safe_area_height + 0.001)

    def test_recto_pages_are_odd(self, base_settings):
        dims = get_page_dimensions(base_settings)
        for page_num in [1, 3, 5, 7]:
            layout = compute_page_layout(base_settings, page_number=page_num, dims=dims)
            assert layout.is_recto, f"Page {page_num} should be recto"

    def test_verso_pages_are_even(self, base_settings):
        dims = get_page_dimensions(base_settings)
        for page_num in [2, 4, 6, 8]:
            layout = compute_page_layout(base_settings, page_number=page_num, dims=dims)
            assert not layout.is_recto, f"Page {page_num} should be verso"

    def test_page_number_stored(self, base_settings):
        dims = get_page_dimensions(base_settings)
        layout = compute_page_layout(base_settings, page_number=5, dims=dims)
        assert layout.page_number == 5

    def test_contains_rect_valid(self, base_settings):
        dims = get_page_dimensions(base_settings)
        layout = compute_page_layout(base_settings, page_number=1, dims=dims)
        # A small rect inside the safe area should pass
        assert layout.contains_rect(
            layout.safe_area_x + 1,
            layout.safe_area_y + 1,
            10,
            10
        )

    def test_contains_rect_overflow(self, base_settings):
        dims = get_page_dimensions(base_settings)
        layout = compute_page_layout(base_settings, page_number=1, dims=dims)
        # A rect larger than the safe area must fail
        assert not layout.contains_rect(0, 0, dims.trim_width * 2, dims.trim_height * 2)

    def test_excessive_margins_raise(self):
        # Use 5x8 page (5" wide) with inner+outer = 5" → safe_w = 0 → ValueError
        settings = BookSettings(
            title="Overflow Test",
            author="Tester",
            trim_size=TrimSize.FIVE_BY_EIGHT,
            puzzle_types=[PuzzleType.SUDOKU],
            margin_inner_in=2.5,
            margin_outer_in=2.5,
        )
        dims = get_page_dimensions(settings)
        with pytest.raises(ValueError, match="too large"):
            compute_page_layout(settings, page_number=1, dims=dims)

    def test_different_page_sizes_produce_different_layouts(self, base_settings):
        settings_6x9 = base_settings.model_copy(update={"trim_size": TrimSize.SIX_BY_NINE})
        settings_8x10 = base_settings.model_copy(update={"trim_size": TrimSize.EIGHT_BY_TEN})
        layout_6x9 = compute_page_layout(settings_6x9, page_number=1)
        layout_8x10 = compute_page_layout(settings_8x10, page_number=1)
        assert layout_6x9.content_width != layout_8x10.content_width
