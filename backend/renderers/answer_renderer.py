"""
Answer Renderer — renders PuzzleData as a colored mosaic (the answer key).

Consumes the SAME PuzzleData as the puzzle renderer. This guarantees
identical grid structure (rows, columns, cell positions, dimensions).

Only the cell content changes: numbers → colors.
Grid lines are rendered as subtle, low-contrast hairlines so the vibrant colors
visually dominate the answer key without overpowering the pixel-art illustration.
"""
from PIL import Image, ImageDraw
from backend.core.puzzle_generator import PuzzleData


def render_answer_image(
    puzzle_data: PuzzleData,
    width: int = 800,
    height: int = 800,
    grid_color: str = "#E0E0E0",
    show_outer_border: bool = True,
) -> Image.Image:
    """Render the answer key (colored mosaic) as a PNG image.

    Uses the EXACT SAME grid structure as the puzzle renderer.
    Same rows, columns, cell positions, cell dimensions, palette.
    Cells are filled with the correct color instead of numbers.

    Args:
        puzzle_data: The SAME puzzle data used by the puzzle renderer.
        width: Output image width in pixels.
        height: Output image height in pixels.
        grid_color: Subtle grid line color (default: low-contrast #E0E0E0).
        show_outer_border: Whether to draw a clean outer bounding box.

    Returns:
        PIL Image of the colored mosaic answer key.
    """
    img = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    gw = puzzle_data.grid_width
    gh = puzzle_data.grid_height

    margin = 20
    available_w = width - 2 * margin
    available_h = height - 2 * margin
    cell_size = min(available_w / gw, available_h / gh)

    grid_w = cell_size * gw
    grid_h = cell_size * gh
    offset_x = (width - grid_w) / 2
    offset_y = (height - grid_h) / 2

    # Draw cells filled with correct colors and subtle hairline grid
    for cell in puzzle_data.cells:
        row = cell["row"]
        col = cell["col"]
        x = offset_x + col * cell_size
        y = offset_y + row * cell_size

        # Fill with the correct color with subtle boundary
        draw.rectangle(
            [x, y, x + cell_size, y + cell_size],
            fill=cell["color_hex"],
            outline=grid_color if cell_size >= 8 else None,
            width=1,
        )

    # Outer border for a clean, professional finish
    if show_outer_border:
        draw.rectangle(
            [offset_x, offset_y, offset_x + grid_w, offset_y + grid_h],
            outline="#999999",
            width=1,
        )

    return img
