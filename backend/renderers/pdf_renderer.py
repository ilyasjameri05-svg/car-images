"""
PDF Renderer — ReportLab-based vector PDF generation for print/KDP quality.

Uses vector grid lines and vector text for crisp, print-ready output.
NO screenshots or raster grids. Every line and number is a vector element.
Answer keys use subtle vector outlines so vibrant mosaic colors dominate the visual appearance.
"""
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white

from backend.core.puzzle_generator import PuzzleData
from backend.renderers.page_layout import PageLayout, calculate_layout


def render_puzzle_pdf(
    puzzle_data: PuzzleData,
    layout: PageLayout,
    title: str = "",
    page_number: int | None = None,
) -> bytes:
    """Render a single puzzle page as a PDF (vector).

    Returns PDF bytes.
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(layout.page_width, layout.page_height))
    c.setTitle(title or "Color-by-Number Puzzle")

    _draw_puzzle_page(c, puzzle_data, layout, title, page_number)

    c.showPage()
    c.save()
    return buf.getvalue()


def render_answer_pdf(
    puzzle_data: PuzzleData,
    layout: PageLayout,
    title: str = "",
    page_number: int | None = None,
) -> bytes:
    """Render a single answer key page as a PDF (vector).

    Uses the SAME PuzzleData — guaranteed identical grid structure.
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(layout.page_width, layout.page_height))
    c.setTitle(title or "Answer Key")

    _draw_answer_page(c, puzzle_data, layout, title, page_number)

    c.showPage()
    c.save()
    return buf.getvalue()


def render_book_pdf(
    puzzles: list[PuzzleData],
    page_size: str = "kdp_8_5x11",
    orientation: str = "portrait",
    answer_key_position: str = "at_end",
    book_title: str = "",
) -> bytes:
    """Render a complete book as a single PDF.

    Args:
        puzzles: List of PuzzleData objects.
        page_size: Page size key.
        orientation: "portrait" or "landscape".
        answer_key_position: "after_each" or "at_end".
        book_title: Book title for the header.

    Returns:
        Complete PDF bytes.
    """
    buf = io.BytesIO()

    # Determine page dimensions
    sample_layout = calculate_layout(
        page_size, orientation,
        puzzles[0].grid_width if puzzles else 30,
        puzzles[0].grid_height if puzzles else 30,
    )
    c = canvas.Canvas(buf, pagesize=(sample_layout.page_width,
                                      sample_layout.page_height))
    c.setTitle(book_title or "Color-by-Number Book")
    c.setAuthor("Color-by-Number Generator")

    page_num = 1

    if answer_key_position == "after_each":
        # Puzzle → Answer for each
        for puzzle in puzzles:
            layout = calculate_layout(
                page_size, orientation,
                puzzle.grid_width, puzzle.grid_height,
                color_count=len(puzzle.palette),
            )
            _draw_puzzle_page(c, puzzle, layout, puzzle.title, page_num)
            c.showPage()
            page_num += 1

            _draw_answer_page(c, puzzle, layout,
                             f"Answer Key - {puzzle.title}" if puzzle.title else "Answer Key",
                             page_num)
            c.showPage()
            page_num += 1
    else:
        # All puzzles first, then all answers
        for puzzle in puzzles:
            layout = calculate_layout(
                page_size, orientation,
                puzzle.grid_width, puzzle.grid_height,
                color_count=len(puzzle.palette),
            )
            _draw_puzzle_page(c, puzzle, layout, puzzle.title, page_num)
            c.showPage()
            page_num += 1

        for puzzle in puzzles:
            layout = calculate_layout(
                page_size, orientation,
                puzzle.grid_width, puzzle.grid_height,
                color_count=len(puzzle.palette),
            )
            _draw_answer_page(c, puzzle, layout,
                             f"Answer Key - {puzzle.title}" if puzzle.title else "Answer Key",
                             page_num)
            c.showPage()
            page_num += 1

    c.save()
    return buf.getvalue()


# ── Internal drawing functions ────────────────────────────────────────

def _draw_puzzle_page(
    c: canvas.Canvas,
    puzzle_data: PuzzleData,
    layout: PageLayout,
    title: str = "",
    page_number: int | None = None,
):
    """Draw a puzzle page on the canvas (numbered grid + color key)."""
    page_h = layout.page_height
    gz = layout.grid_zone
    cell = layout.cell_size

    # Title
    if title:
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(
            layout.title_zone.center_x,
            page_h - layout.title_zone.y - 18,
            title,
        )

    gw = puzzle_data.grid_width
    gh = puzzle_data.grid_height

    # Grid lines — thin crisp vector lines for print quality
    c.setStrokeColor(HexColor("#C0C0C0"))
    c.setLineWidth(0.35)

    # Vertical lines
    for col in range(gw + 1):
        x = gz.x + col * cell
        y_top = page_h - gz.y
        y_bottom = page_h - (gz.y + gh * cell)
        c.line(x, y_top, x, y_bottom)

    # Horizontal lines
    for row in range(gh + 1):
        y = page_h - (gz.y + row * cell)
        c.line(gz.x, y, gz.x + gw * cell, y)

    # Outer border — solid clean boundary
    c.setStrokeColor(HexColor("#666666"))
    c.setLineWidth(0.8)
    c.rect(gz.x, page_h - gz.y - gh * cell, gw * cell, gh * cell, stroke=1, fill=0)

    # Numbers in cells — vector text, centered, scaled to largest safe font size
    max_id = max((cell_data["color_id"] for cell_data in puzzle_data.cells), default=1)
    if max_id >= 10:
        font_size = max(4.0, min(cell * 0.48, 10.5))
    else:
        font_size = max(4.5, min(cell * 0.58, 11.5))

    font_name = "Helvetica-Bold" if cell >= 14.0 else "Helvetica"
    c.setFont(font_name, font_size)
    c.setFillColor(HexColor("#111111"))

    for cell_data in puzzle_data.cells:
        row = cell_data["row"]
        col = cell_data["col"]
        label = str(cell_data["color_id"])

        cx = gz.x + col * cell + cell / 2
        cy = page_h - (gz.y + row * cell + cell / 2)

        # Center the text
        tw = c.stringWidth(label, font_name, font_size)
        c.drawString(cx - tw / 2, cy - font_size * 0.35, label)

    # Color key
    _draw_color_key(c, puzzle_data, layout)

    # Page number
    if page_number is not None:
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#888888"))
        c.drawCentredString(
            layout.page_number_zone.center_x,
            page_h - layout.page_number_zone.y - 12,
            str(page_number),
        )


def _draw_answer_page(
    c: canvas.Canvas,
    puzzle_data: PuzzleData,
    layout: PageLayout,
    title: str = "",
    page_number: int | None = None,
):
    """Draw an answer key page (colored mosaic). Same grid structure as puzzle."""
    page_h = layout.page_height
    gz = layout.grid_zone
    cell = layout.cell_size

    # Title
    if title:
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(
            layout.title_zone.center_x,
            page_h - layout.title_zone.y - 18,
            title,
        )

    gw = puzzle_data.grid_width
    gh = puzzle_data.grid_height

    # Colored cells — subtle hairline stroke so colors visually dominate
    c.setStrokeColor(HexColor("#D8D8D8"))
    c.setLineWidth(0.12)

    for cell_data in puzzle_data.cells:
        row = cell_data["row"]
        col = cell_data["col"]

        x = gz.x + col * cell
        y = page_h - (gz.y + (row + 1) * cell)

        c.setFillColor(HexColor(cell_data["color_hex"]))
        c.rect(x, y, cell, cell, stroke=1, fill=1)

    # Outer border
    c.setStrokeColor(HexColor("#777777"))
    c.setLineWidth(0.8)
    c.rect(gz.x, page_h - gz.y - gh * cell, gw * cell, gh * cell, stroke=1, fill=0)

    # Color key
    _draw_color_key(c, puzzle_data, layout)

    # Page number
    if page_number is not None:
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#888888"))
        c.drawCentredString(
            layout.page_number_zone.center_x,
            page_h - layout.page_number_zone.y - 12,
            str(page_number),
        )


def _draw_color_key(
    c: canvas.Canvas,
    puzzle_data: PuzzleData,
    layout: PageLayout,
):
    """Draw the color key underneath the grid with dynamic columns and crisp swatches."""
    page_h = layout.page_height
    kz = layout.color_key_zone
    palette = puzzle_data.palette

    if not palette:
        return

    cols = getattr(layout, "color_key_cols", 2)
    swatch_size = 9.5
    line_height = 13.5
    col_width = kz.width / cols

    for idx, color in enumerate(palette):
        col_idx = idx % cols
        row_idx = idx // cols

        x = kz.x + col_idx * col_width + 2
        y = page_h - (kz.y + row_idx * line_height + swatch_size + 2)

        # Color swatch with crisp subtle outline
        c.setFillColor(HexColor(color.color_hex))
        c.setStrokeColor(HexColor("#777777"))
        c.setLineWidth(0.35)
        c.rect(x, y, swatch_size, swatch_size, stroke=1, fill=1)

        # Bold number
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor("#111111"))
        num_str = f"{color.color_id}"
        c.drawString(x + swatch_size + 4, y + 2, num_str)
        num_w = c.stringWidth(num_str, "Helvetica-Bold", 8)

        # Color name
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor("#333333"))
        c.drawString(x + swatch_size + 6 + num_w, y + 2, color.color_name)
