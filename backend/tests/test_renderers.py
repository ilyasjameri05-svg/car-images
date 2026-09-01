"""
Tests for renderers (PDF, PNG, SVG) and page layout.
"""
import pytest
from PIL import Image
from backend.core.puzzle_generator import generate_puzzle
from backend.renderers.puzzle_renderer import render_puzzle_image, render_color_key_image
from backend.renderers.answer_renderer import render_answer_image
from backend.renderers.pdf_renderer import render_puzzle_pdf, render_answer_pdf, render_book_pdf
from backend.renderers.png_renderer import render_puzzle_png, render_answer_png
from backend.renderers.svg_renderer import render_puzzle_svg, render_answer_svg
from backend.renderers.page_layout import calculate_layout, PageLayout


class TestPageLayout:
    @pytest.mark.parametrize("page_size", ["a4", "us_letter", "kdp_8_5x11", "kdp_8x10"])
    def test_all_page_sizes(self, page_size):
        layout = calculate_layout(page_size, "portrait", 30, 30)
        assert isinstance(layout, PageLayout)
        assert layout.cell_size > 0
        assert layout.page_width > 0
        assert layout.page_height > 0

    def test_portrait_orientation(self):
        layout = calculate_layout("kdp_8_5x11", "portrait", 30, 30)
        assert layout.page_height > layout.page_width

    def test_landscape_orientation(self):
        layout = calculate_layout("kdp_8_5x11", "landscape", 30, 30)
        assert layout.page_width > layout.page_height

    def test_grid_fits_within_margins(self):
        layout = calculate_layout("kdp_8_5x11", "portrait", 30, 30)
        gz = layout.grid_zone
        assert gz.x >= layout.margin_inside
        assert gz.right <= layout.page_width - layout.margin_outside
        assert gz.y >= layout.margin_top

    def test_square_cells(self):
        """Cell size should produce square cells."""
        layout = calculate_layout("kdp_8_5x11", "portrait", 30, 30)
        # Cell size is a single value = square
        assert layout.cell_size > 0

    def test_decoration_zones_outside_grid(self):
        """Decoration zones must not overlap with the grid zone."""
        layout = calculate_layout("kdp_8_5x11", "portrait", 30, 30)
        gz = layout.grid_zone
        for dz in layout.decoration_zones:
            # Decoration zone should not overlap grid
            overlaps_x = dz.x < gz.right and dz.right > gz.x
            overlaps_y = dz.y < gz.bottom and dz.bottom > gz.y
            assert not (overlaps_x and overlaps_y), "Decoration zone overlaps grid!"


class TestPuzzleRenderer:
    def test_render_puzzle_image(self, sample_image):
        puzzle = generate_puzzle(sample_image, 20, 20, 6, seed=42)
        img = render_puzzle_image(puzzle, 400, 400)
        assert isinstance(img, Image.Image)
        assert img.size == (400, 400)

    def test_render_color_key(self, sample_image):
        puzzle = generate_puzzle(sample_image, 20, 20, 6, seed=42)
        img = render_color_key_image(puzzle, 400, 60)
        assert isinstance(img, Image.Image)


class TestAnswerRenderer:
    def test_render_answer_image(self, sample_image):
        puzzle = generate_puzzle(sample_image, 20, 20, 6, seed=42)
        img = render_answer_image(puzzle, 400, 400)
        assert isinstance(img, Image.Image)
        assert img.size == (400, 400)


class TestPDFRenderer:
    def test_render_puzzle_pdf(self, sample_image):
        puzzle = generate_puzzle(sample_image, 20, 20, 6, seed=42)
        layout = calculate_layout("kdp_8_5x11", "portrait", 20, 20)
        pdf_bytes = render_puzzle_pdf(puzzle, layout, "Test Puzzle")
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:5] == b'%PDF-'

    def test_render_answer_pdf(self, sample_image):
        puzzle = generate_puzzle(sample_image, 20, 20, 6, seed=42)
        layout = calculate_layout("kdp_8_5x11", "portrait", 20, 20)
        pdf_bytes = render_answer_pdf(puzzle, layout, "Answer Key")
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:5] == b'%PDF-'

    def test_render_book_pdf(self, sample_image):
        puzzles = [
            generate_puzzle(sample_image, 20, 20, 6, seed=i)
            for i in range(3)
        ]
        pdf_bytes = render_book_pdf(puzzles, "kdp_8_5x11", "portrait", "at_end")
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:5] == b'%PDF-'

    def test_render_book_after_each(self, sample_image):
        puzzles = [generate_puzzle(sample_image, 20, 20, 6, seed=42)]
        pdf_bytes = render_book_pdf(puzzles, "kdp_8_5x11", "portrait", "after_each")
        assert len(pdf_bytes) > 0


class TestPNGRenderer:
    def test_render_puzzle_png(self, sample_image):
        puzzle = generate_puzzle(sample_image, 20, 20, 6, seed=42)
        png_bytes = render_puzzle_png(puzzle, dpi=72,
                                       page_width_inches=8.5,
                                       page_height_inches=11.0)
        assert len(png_bytes) > 0
        assert png_bytes[:4] == b'\x89PNG'

    def test_render_answer_png(self, sample_image):
        puzzle = generate_puzzle(sample_image, 20, 20, 6, seed=42)
        png_bytes = render_answer_png(puzzle, dpi=72,
                                       page_width_inches=8.5,
                                       page_height_inches=11.0)
        assert len(png_bytes) > 0


class TestSVGRenderer:
    def test_render_puzzle_svg(self, sample_image):
        puzzle = generate_puzzle(sample_image, 20, 20, 6, seed=42)
        svg_str = render_puzzle_svg(puzzle)
        assert '<svg' in svg_str
        assert 'xmlns' in svg_str
        assert len(svg_str) > 100

    def test_render_answer_svg(self, sample_image):
        puzzle = generate_puzzle(sample_image, 20, 20, 6, seed=42)
        svg_str = render_answer_svg(puzzle)
        assert '<svg' in svg_str
