"""
Puzzle Renderer — renders PuzzleData as a numbered grid (the puzzle page).

Consumes PuzzleData (never reprocesses the source image).
Numbers are sharp, high-contrast, centered in each cell, and scaled to the
largest safe font size to ensure legibility when printed.
"""
from PIL import Image, ImageDraw, ImageFont
from backend.core.puzzle_generator import PuzzleData


def render_puzzle_image(
    puzzle_data: PuzzleData,
    width: int = 800,
    height: int = 800,
    bg_color: str = "#FFFFFF",
    grid_color: str = "#BDBDBD",
    text_color: str = "#111111",
) -> Image.Image:
    """Render the puzzle (numbered grid) as a PNG image.

    Args:
        puzzle_data: The puzzle data (generated once, shared with answer renderer).
        width: Output image width in pixels.
        height: Output image height in pixels.
        bg_color: Cell background color.
        grid_color: Grid border color.
        text_color: Number text color.

    Returns:
        PIL Image of the numbered mosaic grid.
    """
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    gw = puzzle_data.grid_width
    gh = puzzle_data.grid_height

    # Calculate cell size (square cells)
    margin = 20
    available_w = width - 2 * margin
    available_h = height - 2 * margin
    cell_size = min(available_w / gw, available_h / gh)

    # Center the grid
    grid_w = cell_size * gw
    grid_h = cell_size * gh
    offset_x = (width - grid_w) / 2
    offset_y = (height - grid_h) / 2

    # Determine largest safe font size — accounting for 1-digit vs 2-digit numbers
    max_id = max((c["color_id"] for c in puzzle_data.cells), default=1)
    if max_id >= 10:
        font_size = max(7, int(cell_size * 0.48))
    else:
        font_size = max(8, int(cell_size * 0.58))

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

    # Draw cells with numbers
    for cell in puzzle_data.cells:
        row = cell["row"]
        col = cell["col"]
        x = offset_x + col * cell_size
        y = offset_y + row * cell_size

        # Cell border
        draw.rectangle(
            [x, y, x + cell_size, y + cell_size],
            outline=grid_color, width=1
        )

        # Number centered with exact bounding box calculation
        label = str(cell["color_id"])
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = x + (cell_size - tw) / 2 - bbox[0]
        ty = y + (cell_size - th) / 2 - bbox[1]
        draw.text((tx, ty), label, fill=text_color, font=font)

    # Outer border for crisp finish
    draw.rectangle(
        [offset_x, offset_y, offset_x + grid_w, offset_y + grid_h],
        outline="#666666",
        width=1,
    )

    return img


def render_color_key_image(
    puzzle_data: PuzzleData,
    width: int = 800,
    height: int = 100,
) -> Image.Image:
    """Render the color key as a crisp, well-aligned image strip."""
    palette = puzzle_data.palette
    n = len(palette)
    cols = 4 if n >= 12 else (3 if n >= 7 else 2)
    rows_needed = (n + cols - 1) // cols

    img = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    swatch_size = 14
    padding_x = 12
    padding_y = 6
    col_width = (width - padding_x * 2) // cols

    font_size = 11
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
        font_bold = ImageFont.truetype("arialbd.ttf", font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()
        font_bold = font

    for idx, color in enumerate(palette):
        col_idx = idx % cols
        row_idx = idx // cols
        x = padding_x + col_idx * col_width
        y = padding_y + row_idx * (swatch_size + padding_y)

        # Color swatch with crisp border so light colors are clear
        draw.rectangle(
            [x, y, x + swatch_size, y + swatch_size],
            fill=color.color_hex,
            outline="#777777",
            width=1,
        )

        # Label: "1 Black"
        id_str = f"{color.color_id}"
        draw.text((x + swatch_size + 6, y + 1), id_str, fill="#111111", font=font_bold)
        
        # Calculate offset for name
        id_bbox = draw.textbbox((0, 0), id_str, font=font_bold)
        id_w = id_bbox[2] - id_bbox[0]
        name_str = f" {color.color_name}"
        draw.text((x + swatch_size + 8 + id_w, y + 1), name_str, fill="#333333", font=font)

    return img
