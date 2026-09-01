"""
SVG Renderer — svgwrite-based vector SVG export.

Perfect for further editing in design tools (Illustrator, Inkscape, etc.)
Answer keys use subtle hairline borders so vibrant colors visually dominate.
"""
import io
import svgwrite

from backend.core.puzzle_generator import PuzzleData


def render_puzzle_svg(
    puzzle_data: PuzzleData,
    width_mm: float = 215.9,   # 8.5 inches
    height_mm: float = 279.4,  # 11 inches
) -> str:
    """Render puzzle as SVG (vector). Returns SVG string."""
    gw = puzzle_data.grid_width
    gh = puzzle_data.grid_height

    # Calculate dimensions with margins
    margin = 15  # mm
    available_w = width_mm - 2 * margin
    available_h = height_mm - 2 * margin - 30  # reserve for color key

    cell_size = min(available_w / gw, available_h / gh)
    grid_w = cell_size * gw
    grid_h = cell_size * gh
    offset_x = margin + (available_w - grid_w) / 2
    offset_y = margin + 14  # space for title

    dwg = svgwrite.Drawing(
        size=(f"{width_mm}mm", f"{height_mm}mm"),
        viewBox=f"0 0 {width_mm} {height_mm}",
    )

    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=(width_mm, height_mm), fill="white"))

    # Title
    if puzzle_data.title:
        dwg.add(dwg.text(
            puzzle_data.title,
            insert=(width_mm / 2, margin + 5),
            text_anchor="middle",
            font_size="5mm",
            font_family="Helvetica, Arial, sans-serif",
            font_weight="bold",
            fill="#111111",
        ))

    # Grid cells with numbers
    max_id = max((c["color_id"] for c in puzzle_data.cells), default=1)
    if max_id >= 10:
        font_size = max(1.2, cell_size * 0.46)
    else:
        font_size = max(1.4, cell_size * 0.56)

    for cell_data in puzzle_data.cells:
        row = cell_data["row"]
        col = cell_data["col"]
        x = offset_x + col * cell_size
        y = offset_y + row * cell_size

        # Cell border
        dwg.add(dwg.rect(
            insert=(x, y), size=(cell_size, cell_size),
            fill="white", stroke="#BDBDBD", stroke_width=0.12,
        ))

        # Number centered
        label = str(cell_data["color_id"])
        dwg.add(dwg.text(
            label,
            insert=(x + cell_size / 2, y + cell_size / 2 + font_size * 0.35),
            text_anchor="middle",
            font_size=f"{font_size}mm",
            font_family="Helvetica, Arial, sans-serif",
            fill="#111111",
        ))

    # Outer border
    dwg.add(dwg.rect(
        insert=(offset_x, offset_y), size=(grid_w, grid_h),
        fill="none", stroke="#666666", stroke_width=0.3,
    ))

    # Color key
    key_y = offset_y + grid_h + 5
    _draw_svg_color_key(dwg, puzzle_data, offset_x, key_y, grid_w)

    return dwg.tostring()


def render_answer_svg(
    puzzle_data: PuzzleData,
    width_mm: float = 215.9,
    height_mm: float = 279.4,
) -> str:
    """Render answer key as SVG (vector). Returns SVG string."""
    gw = puzzle_data.grid_width
    gh = puzzle_data.grid_height

    margin = 15
    available_w = width_mm - 2 * margin
    available_h = height_mm - 2 * margin - 30

    cell_size = min(available_w / gw, available_h / gh)
    grid_w = cell_size * gw
    grid_h = cell_size * gh
    offset_x = margin + (available_w - grid_w) / 2
    offset_y = margin + 14

    dwg = svgwrite.Drawing(
        size=(f"{width_mm}mm", f"{height_mm}mm"),
        viewBox=f"0 0 {width_mm} {height_mm}",
    )

    dwg.add(dwg.rect(insert=(0, 0), size=(width_mm, height_mm), fill="white"))

    # Title
    title = f"Answer Key - {puzzle_data.title}" if puzzle_data.title else "Answer Key"
    dwg.add(dwg.text(
        title,
        insert=(width_mm / 2, margin + 5),
        text_anchor="middle",
        font_size="5mm",
        font_family="Helvetica, Arial, sans-serif",
        font_weight="bold",
        fill="#111111",
    ))

    # Colored cells with subtle hairline outline
    for cell_data in puzzle_data.cells:
        row = cell_data["row"]
        col = cell_data["col"]
        x = offset_x + col * cell_size
        y = offset_y + row * cell_size

        dwg.add(dwg.rect(
            insert=(x, y), size=(cell_size, cell_size),
            fill=cell_data["color_hex"],
            stroke="#D8D8D8", stroke_width=0.06,
        ))

    # Outer border
    dwg.add(dwg.rect(
        insert=(offset_x, offset_y), size=(grid_w, grid_h),
        fill="none", stroke="#777777", stroke_width=0.3,
    ))

    # Color key
    key_y = offset_y + grid_h + 5
    _draw_svg_color_key(dwg, puzzle_data, offset_x, key_y, grid_w)

    return dwg.tostring()


def _draw_svg_color_key(
    dwg: svgwrite.Drawing,
    puzzle_data: PuzzleData,
    x: float,
    y: float,
    width: float,
):
    """Draw color key in SVG with dynamic columns and crisp swatches."""
    palette = puzzle_data.palette
    n = len(palette)
    cols = 4 if n >= 15 else (3 if n >= 9 else 2)
    col_width = width / cols
    swatch_size = 3.5
    line_height = 5

    for idx, color in enumerate(palette):
        col_idx = idx % cols
        row_idx = idx // cols
        sx = x + col_idx * col_width + 1
        sy = y + row_idx * line_height

        # Swatch with crisp border
        dwg.add(dwg.rect(
            insert=(sx, sy), size=(swatch_size, swatch_size),
            fill=color.color_hex, stroke="#777777", stroke_width=0.1,
        ))

        # Bold number + name
        dwg.add(dwg.text(
            f"{color.color_id} {color.color_name}",
            insert=(sx + swatch_size + 2, sy + swatch_size * 0.8),
            font_size="2.4mm",
            font_family="Helvetica, Arial, sans-serif",
            fill="#222222",
        ))
