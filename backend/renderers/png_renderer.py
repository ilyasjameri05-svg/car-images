"""
PNG Renderer — high-resolution raster export (300 DPI for print).
"""
import io
from PIL import Image

from backend.core.puzzle_generator import PuzzleData
from backend.renderers.puzzle_renderer import render_puzzle_image, render_color_key_image
from backend.renderers.answer_renderer import render_answer_image


def render_puzzle_png(
    puzzle_data: PuzzleData,
    dpi: int = 300,
    page_width_inches: float = 8.5,
    page_height_inches: float = 11.0,
) -> bytes:
    """Render puzzle as a high-resolution PNG."""
    width = int(page_width_inches * dpi)
    height = int(page_height_inches * dpi)

    # Grid takes 78% of the page height
    grid_height = int(height * 0.78)
    grid_img = render_puzzle_image(puzzle_data, width, grid_height)

    # Color key takes remaining space
    key_height = int(height * 0.12)
    key_img = render_color_key_image(puzzle_data, width, key_height)

    # Compose onto a full page
    page = Image.new("RGB", (width, height), "#FFFFFF")
    page.paste(grid_img, (0, int(height * 0.05)))
    page.paste(key_img, (0, int(height * 0.85)))

    buf = io.BytesIO()
    page.save(buf, format="PNG", dpi=(dpi, dpi))
    return buf.getvalue()


def render_answer_png(
    puzzle_data: PuzzleData,
    dpi: int = 300,
    page_width_inches: float = 8.5,
    page_height_inches: float = 11.0,
) -> bytes:
    """Render answer key as a high-resolution PNG."""
    width = int(page_width_inches * dpi)
    height = int(page_height_inches * dpi)

    grid_height = int(height * 0.78)
    answer_img = render_answer_image(puzzle_data, width, grid_height)

    key_height = int(height * 0.12)
    key_img = render_color_key_image(puzzle_data, width, key_height)

    page = Image.new("RGB", (width, height), "#FFFFFF")
    page.paste(answer_img, (0, int(height * 0.05)))
    page.paste(key_img, (0, int(height * 0.85)))

    buf = io.BytesIO()
    page.save(buf, format="PNG", dpi=(dpi, dpi))
    return buf.getvalue()
