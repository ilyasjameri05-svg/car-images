"""
ReportLab-based page renderer for all puzzle types and answer keys.

Design principles:
- All coordinates come from the PageLayout engine.
- All content is vector-based (no rasterised page images).
- Every render method receives a validated PuzzleRecord.
- Nothing overflows the safe area; the layout engine enforces this first.
"""
from __future__ import annotations

import math
from typing import List, Optional

from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.pdfgen.canvas import Canvas

from app.models.book import BookSettings
from app.models.layout import PageLayout, POINTS_PER_INCH
from app.models.puzzle import PuzzleRecord

Grid = List[List[int]]

# ---------------------------------------------------------------------------
# Visual constants
# ---------------------------------------------------------------------------
_GIVEN_FONT_SIZE    = 18
_HEADER_FONT_SIZE   = 9
_FOOTER_FONT_SIZE   = 8
_INSTRUCTION_FONT_SIZE = 9
_ANSWER_SMALL_FONT  = 6

_GIVEN_BG         = HexColor("#F0F0F0")
_BOX_BORDER_COLOR = black
_CELL_BORDER_COLOR = HexColor("#888888")
_GRID_LINE_THIN   = 0.5
_GRID_LINE_THICK  = 1.8

_ACCENT      = HexColor("#2C3E50")
_LIGHT_GREY  = HexColor("#EEEEEE")
_MID_GREY    = HexColor("#AAAAAA")
_DARK_GREY   = HexColor("#555555")


class PageRenderer:
    """Renders a complete puzzle page or answer-key page onto a ReportLab Canvas."""

    def __init__(self, settings: BookSettings) -> None:
        self.settings = settings

    # ======================================================================
    # Public routing entry points
    # ======================================================================

    def render_puzzle_page(self, canvas: Canvas, layout: PageLayout,
                           record: PuzzleRecord) -> None:
        """Route to the correct puzzle renderer by type."""
        pt = record.puzzle_type
        if pt == "sudoku":
            self.render_sudoku_page(canvas, layout, record)
        elif pt == "word_search":
            self._render_word_search_page(canvas, layout, record)
        elif pt == "maze":
            self._render_maze_page(canvas, layout, record)
        elif pt == "logic_grid":
            self._render_logic_grid_page(canvas, layout, record)
        elif pt == "code_breaker":
            self._render_code_breaker_page(canvas, layout, record)
        elif pt == "matching":
            self._render_matching_page(canvas, layout, record)
        elif pt == "pattern":
            self._render_pattern_page(canvas, layout, record)
        elif pt == "critical_thinking":
            self._render_critical_thinking_page(canvas, layout, record)
        elif pt == "picture_puzzle":
            self._render_picture_puzzle_page(canvas, layout, record)
        elif pt == "escape_room":
            self._render_escape_room_page(canvas, layout, record)
        else:
            self._render_placeholder(canvas, layout, record)

    def render_answer_key_entry(self, canvas: Canvas, x: float, y: float,
                                w: float, h: float, record: PuzzleRecord,
                                page_num: Optional[int] = None) -> None:
        """Render one answer-key block for any puzzle type."""
        pt = record.puzzle_type
        if pt == "sudoku":
            self._draw_mini_sudoku_answer(canvas, record, x, y, w, h)
        elif pt == "word_search":
            self._draw_mini_word_search_answer(canvas, record, x, y, w, h)
        elif pt == "maze":
            self._draw_mini_maze_answer(canvas, record, x, y, w, h)
        else:
            self._draw_text_answer_block(canvas, record, x, y, w, h)

    # ======================================================================
    # Sudoku (from Phase 2)
    # ======================================================================

    def render_sudoku_page(self, canvas: Canvas, layout: PageLayout,
                           record: PuzzleRecord) -> None:
        self._draw_puzzle_header(canvas, layout, record)
        self._draw_footer(canvas, layout)
        self._draw_instructions(canvas, layout, record.instructions)
        self._draw_sudoku_grid(canvas, layout, record)

    # ======================================================================
    # Word Search
    # ======================================================================

    def _render_word_search_page(self, canvas: Canvas, layout: PageLayout,
                                  record: PuzzleRecord) -> None:
        self._draw_puzzle_header(canvas, layout, record)
        self._draw_footer(canvas, layout)
        self._draw_instructions(canvas, layout, record.instructions)

        d = record.puzzle_data
        grid = d["grid"]
        words = d["words"]
        size = d["grid_size"]

        # Reserve bottom area for word list
        word_list_height = math.ceil(len(words) / 4) * 14 + 10
        available_h = layout.content_height - 30 - word_list_height
        available_w = layout.content_width

        cell_size = min(available_w / size, available_h / size)
        grid_w = cell_size * size
        grid_h = cell_size * size
        grid_x = layout.content_x + (layout.content_width - grid_w) / 2
        grid_y = layout.content_y + word_list_height + (available_h - grid_h) / 2

        # Draw cells
        font_size = min(cell_size * 0.55, 11)
        for row in range(size):
            for col in range(size):
                cx = grid_x + col * cell_size
                cy = grid_y + (size - 1 - row) * cell_size
                canvas.setFillColor(white)
                canvas.rect(cx, cy, cell_size, cell_size, stroke=0, fill=1)
                canvas.setFillColor(black)
                canvas.setFont("Helvetica-Bold", font_size)
                canvas.drawCentredString(
                    cx + cell_size / 2,
                    cy + cell_size / 2 - font_size * 0.35,
                    grid[row][col]
                )

        # Grid border lines
        canvas.setStrokeColor(_CELL_BORDER_COLOR)
        canvas.setLineWidth(0.3)
        for i in range(size + 1):
            y_pos = grid_y + i * cell_size
            canvas.line(grid_x, y_pos, grid_x + grid_w, y_pos)
            x_pos = grid_x + i * cell_size
            canvas.line(x_pos, grid_y, x_pos, grid_y + grid_h)

        # Outer border
        canvas.setStrokeColor(black)
        canvas.setLineWidth(1.5)
        canvas.rect(grid_x, grid_y, grid_w, grid_h, stroke=1, fill=0)

        # Word list below grid
        self._draw_word_list(canvas, layout, words, word_list_height)

    def _draw_word_list(self, canvas: Canvas, layout: PageLayout,
                        words: List[str], reserved_height: float) -> None:
        """Draw words in 4 columns at the bottom of the content area."""
        x0 = layout.content_x
        y0 = layout.content_y + 4
        cols = 4
        col_w = layout.content_width / cols
        canvas.setFont("Helvetica-Bold", 7)
        canvas.setFillColor(_DARK_GREY)
        canvas.drawString(x0, y0 + reserved_height - 12, "Find these words:")
        canvas.setFont("Helvetica", 8)
        for i, word in enumerate(sorted(words)):
            col = i % cols
            row = i // cols
            wx = x0 + col * col_w
            wy = y0 + reserved_height - 26 - row * 12
            canvas.drawString(wx, wy, f"☐  {word}")

    # ======================================================================
    # Maze
    # ======================================================================

    def _render_maze_page(self, canvas: Canvas, layout: PageLayout,
                           record: PuzzleRecord) -> None:
        self._draw_puzzle_header(canvas, layout, record)
        self._draw_footer(canvas, layout)
        self._draw_instructions(canvas, layout, record.instructions)
        self._draw_maze_grid(canvas, layout, record)

    def _draw_maze_grid(self, canvas: Canvas, layout: PageLayout,
                        record: PuzzleRecord) -> None:
        d = record.puzzle_data
        walls = d["walls"]
        rows, cols = d["rows"], d["cols"]
        start = d["start"]
        end   = d["end"]

        available_h = layout.content_height - 30
        available_w = layout.content_width
        cell_size = min(available_w / cols, available_h / rows)
        maze_w = cell_size * cols
        maze_h = cell_size * rows
        gx = layout.content_x + (layout.content_width - maze_w) / 2
        gy = layout.content_y + (available_h - maze_h) / 2

        canvas.setStrokeColor(black)
        canvas.setLineWidth(0.8)

        for r in range(rows):
            for c in range(cols):
                cx = gx + c * cell_size
                cy = gy + (rows - 1 - r) * cell_size
                w = walls[r][c]

                if w["N"]:
                    canvas.line(cx, cy + cell_size, cx + cell_size, cy + cell_size)
                if w["S"]:
                    canvas.line(cx, cy, cx + cell_size, cy)
                if w["E"]:
                    canvas.line(cx + cell_size, cy, cx + cell_size, cy + cell_size)
                if w["W"]:
                    canvas.line(cx, cy, cx, cy + cell_size)

        # START / FINISH labels
        canvas.setFont("Helvetica-Bold", min(cell_size * 0.5, 8))
        canvas.setFillColor(_ACCENT)
        sr, sc = start
        er, ec = end
        start_x = gx + sc * cell_size + cell_size / 2
        start_y = gy + (rows - 1 - sr) * cell_size + cell_size / 2 - 3
        end_x   = gx + ec * cell_size + cell_size / 2
        end_y   = gy + (rows - 1 - er) * cell_size + cell_size / 2 - 3
        canvas.drawCentredString(start_x, start_y, "S")
        canvas.drawCentredString(end_x, end_y, "F")
        canvas.setFillColor(black)

    # ======================================================================
    # Logic Grid
    # ======================================================================

    def _render_logic_grid_page(self, canvas: Canvas, layout: PageLayout,
                                 record: PuzzleRecord) -> None:
        self._draw_puzzle_header(canvas, layout, record)
        self._draw_footer(canvas, layout)
        self._draw_instructions(canvas, layout, record.instructions)

        d = record.puzzle_data
        people     = d["items"][d["primary"]]
        other_cats = d["other_cats"]
        clues      = d["clues"]
        n          = d["num_items"]

        # Available area
        top_y  = layout.content_y + layout.content_height - 30
        clue_h = len(clues) * 13 + 20
        grid_h = min((layout.content_height - 30 - clue_h) * 0.9, 220)
        grid_w = min(layout.content_width * 0.9, 280)

        # Draw the logic grid matrix
        cols_count = n * (len(other_cats))  # columns for all non-primary categories
        row_h = grid_h / (n + 1)            # +1 for header row
        col_w = grid_w / (cols_count + 1)   # +1 for person labels

        gx = layout.content_x + (layout.content_width - grid_w) / 2
        gy = top_y - grid_h

        canvas.setStrokeColor(_MID_GREY)
        canvas.setLineWidth(0.4)

        # Draw grid cells
        for r in range(n + 1):
            for c in range(cols_count + 1):
                cx = gx + c * col_w
                cy = gy + (n - r) * row_h
                canvas.rect(cx, cy, col_w, row_h, stroke=1, fill=0)

        # Header labels (category + item names)
        canvas.setFont("Helvetica-Bold", min(col_w * 0.35, 7))
        canvas.setFillColor(_ACCENT)
        col_idx = 1
        for cat in other_cats:
            items = d["items"][cat]
            for item in items:
                cx = gx + col_idx * col_w + col_w / 2
                cy = gy + n * row_h + row_h / 2 - 4
                canvas.drawCentredString(cx, cy, item[:6])
                col_idx += 1

        # Person labels
        canvas.setFont("Helvetica", min(col_w * 0.35, 7))
        canvas.setFillColor(black)
        for ri, person in enumerate(people):
            cx = gx + col_w / 2
            cy = gy + (n - 1 - ri) * row_h + row_h / 2 - 3
            canvas.drawCentredString(cx, cy, person[:8])

        # Clues
        clue_y = gy - 16
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(_ACCENT)
        canvas.drawString(gx, clue_y, "Clues:")
        clue_y -= 13
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(black)
        for i, clue in enumerate(clues):
            if clue_y < layout.content_y:
                break
            canvas.drawString(gx, clue_y, f"{i+1}. {clue}")
            clue_y -= 13

    # ======================================================================
    # Code Breaker
    # ======================================================================

    def _render_code_breaker_page(self, canvas: Canvas, layout: PageLayout,
                                   record: PuzzleRecord) -> None:
        self._draw_puzzle_header(canvas, layout, record)
        self._draw_footer(canvas, layout)
        self._draw_instructions(canvas, layout, record.instructions)

        d = record.puzzle_data
        encoded = d["encoded"]
        alpha   = d["alphabet_table"]
        revealed = d.get("revealed_indices", [])
        hint    = d.get("hint", "")

        x = layout.content_x
        y = layout.content_y + layout.content_height - 30

        # Hint line
        if hint:
            canvas.setFont("Helvetica-Oblique", 9)
            canvas.setFillColor(_ACCENT)
            canvas.drawString(x, y, hint)
            y -= 18

        # Encoded message (large, spaced out)
        canvas.setFont("Courier-Bold", 14)
        canvas.setFillColor(black)
        max_w = layout.content_width
        # Word-wrap encoded message
        words = encoded.split()
        line = ""
        for word in words:
            test = (line + " " + word).strip()
            if canvas.stringWidth(test, "Courier-Bold", 14) < max_w:
                line = test
            else:
                canvas.drawString(x, y, line)
                y -= 20
                line = word
        if line:
            canvas.drawString(x, y, line)
        y -= 30

        # Decoder table (26 letters in 2 rows of 13)
        canvas.setFont("Helvetica-Bold", 7)
        canvas.setFillColor(_ACCENT)
        canvas.drawString(x, y, "Cipher alphabet:")
        y -= 14

        table_cols = 13
        cell_w = layout.content_width / table_cols
        cell_h = 22

        for row_start in [0, 13]:
            for i in range(table_cols):
                idx = row_start + i
                if idx >= 26:
                    break
                cx = x + i * cell_w
                plain_char  = alpha[idx]["plain"]
                cipher_char = alpha[idx]["cipher"]
                is_revealed = idx in revealed

                # Plain letter header
                canvas.setFillColor(_LIGHT_GREY)
                canvas.rect(cx, y, cell_w, cell_h / 2, stroke=1, fill=1)
                canvas.setFillColor(_ACCENT)
                canvas.setFont("Helvetica-Bold", 7)
                canvas.drawCentredString(cx + cell_w / 2, y + cell_h / 4 - 3, plain_char)

                # Cipher cell (show if revealed)
                canvas.setFillColor(HexColor("#FFF9C4") if is_revealed else white)
                canvas.rect(cx, y - cell_h / 2, cell_w, cell_h / 2, stroke=1, fill=1)
                if is_revealed:
                    canvas.setFillColor(_DARK_GREY)
                    canvas.drawCentredString(cx + cell_w / 2, y - cell_h / 2 + cell_h / 4 - 3, cipher_char)

            y -= cell_h + 6

        # Decode workspace lines
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(_MID_GREY)
        canvas.drawString(x, y - 8, "Write your decoded message below:")
        for _ in range(3):
            y -= 20
            if y > layout.content_y:
                canvas.setStrokeColor(_LIGHT_GREY)
                canvas.setLineWidth(0.5)
                canvas.line(x, y, x + layout.content_width, y)

    # ======================================================================
    # Matching
    # ======================================================================

    def _render_matching_page(self, canvas: Canvas, layout: PageLayout,
                               record: PuzzleRecord) -> None:
        self._draw_puzzle_header(canvas, layout, record)
        self._draw_footer(canvas, layout)
        self._draw_instructions(canvas, layout, record.instructions)

        d = record.puzzle_data
        left  = d["left_items"]
        right = d["right_items"]

        x = layout.content_x
        y = layout.content_y + layout.content_height - 30
        col_w = layout.content_width / 2 - 20
        row_h = min(30, (layout.content_height - 40) / max(len(left), 1))

        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(_ACCENT)
        canvas.drawString(x, y, "Column A")
        canvas.drawRightString(x + layout.content_width, y, "Column B")
        y -= 16

        for i, (l_item, r_item) in enumerate(zip(left, right)):
            item_y = y - i * row_h
            if item_y < layout.content_y:
                break

            # Left box
            canvas.setFillColor(_LIGHT_GREY)
            canvas.roundRect(x, item_y - row_h + 4, col_w, row_h - 4, 3, stroke=1, fill=1)
            canvas.setFillColor(black)
            canvas.setFont("Helvetica", 9)
            canvas.drawString(x + 6, item_y - row_h / 2 - 3, f"{i+1}.  {l_item}")

            # Right box
            rx = x + layout.content_width - col_w
            canvas.setFillColor(_LIGHT_GREY)
            canvas.roundRect(rx, item_y - row_h + 4, col_w, row_h - 4, 3, stroke=1, fill=1)
            canvas.setFillColor(black)
            canvas.drawString(rx + 6, item_y - row_h / 2 - 3,
                               f"{chr(65 + i)}.  {r_item}")

            # Answer blank
            mid_x = x + col_w + 6
            canvas.setStrokeColor(_MID_GREY)
            canvas.setLineWidth(0.4)
            canvas.line(mid_x, item_y - row_h + 6, mid_x + 8, item_y - row_h + 6)

    # ======================================================================
    # Pattern
    # ======================================================================

    def _render_pattern_page(self, canvas: Canvas, layout: PageLayout,
                              record: PuzzleRecord) -> None:
        self._draw_puzzle_header(canvas, layout, record)
        self._draw_footer(canvas, layout)
        self._draw_instructions(canvas, layout, record.instructions)

        d = record.puzzle_data
        sequences = d["sequences"]

        x = layout.content_x
        y = layout.content_y + layout.content_height - 30
        row_h = min(55, (layout.content_height - 40) / max(len(sequences), 1))

        for i, seq in enumerate(sequences):
            item_y = y - i * row_h
            if item_y - row_h < layout.content_y:
                break

            display = seq["display"]
            rule    = seq["rule"]

            # Sequence number
            canvas.setFont("Helvetica-Bold", 9)
            canvas.setFillColor(_ACCENT)
            canvas.drawString(x, item_y, f"{i+1}.")

            # Draw sequence boxes
            num_boxes = len(display)
            box_w = min(40, (layout.content_width - 20) / num_boxes)
            box_h = 24
            start_x = x + 20

            for j, val in enumerate(display):
                bx = start_x + j * (box_w + 4)
                by = item_y - box_h - 2

                is_blank = (val == "___")
                canvas.setFillColor(_LIGHT_GREY if not is_blank else HexColor("#FFF9C4"))
                canvas.rect(bx, by, box_w, box_h, stroke=1, fill=1)

                if not is_blank:
                    canvas.setFillColor(black)
                    canvas.setFont("Helvetica-Bold", 10)
                    canvas.drawCentredString(
                        bx + box_w / 2,
                        by + box_h / 2 - 5,
                        str(val)
                    )

            # Rule hint
            canvas.setFont("Helvetica-Oblique", 7)
            canvas.setFillColor(_MID_GREY)
            canvas.drawString(
                start_x,
                item_y - box_h - 16,
                f"Rule: {rule}"
            )

    # ======================================================================
    # Critical Thinking
    # ======================================================================

    def _render_critical_thinking_page(self, canvas: Canvas, layout: PageLayout,
                                        record: PuzzleRecord) -> None:
        self._draw_puzzle_header(canvas, layout, record)
        self._draw_footer(canvas, layout)

        d = record.puzzle_data
        question = d["question"]

        x = layout.content_x
        w = layout.content_width
        y = layout.content_y + layout.content_height - 20

        # Question box
        q_lines = self._wrap_text(canvas, question, "Helvetica", 11, w - 20)
        box_h = len(q_lines) * 15 + 24
        box_y = y - box_h
        canvas.setFillColor(_LIGHT_GREY)
        canvas.roundRect(x, box_y, w, box_h, 5, stroke=1, fill=1)
        canvas.setFillColor(black)
        canvas.setFont("Helvetica", 11)
        for i, line in enumerate(q_lines):
            canvas.drawString(x + 10, y - 16 - i * 15, line)

        # Answer area
        ans_y = box_y - 30
        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(_ACCENT)
        canvas.drawString(x, ans_y, "My answer:")
        for i in range(3):
            line_y = ans_y - 20 - i * 22
            if line_y > layout.content_y:
                canvas.setStrokeColor(_CELL_BORDER_COLOR)
                canvas.setLineWidth(0.6)
                canvas.line(x, line_y, x + w, line_y)

    # ======================================================================
    # Picture Puzzle
    # ======================================================================

    def _render_picture_puzzle_page(self, canvas: Canvas, layout: PageLayout,
                                     record: PuzzleRecord) -> None:
        self._draw_puzzle_header(canvas, layout, record)
        self._draw_footer(canvas, layout)
        self._draw_instructions(canvas, layout, record.instructions)

        d = record.puzzle_data
        grid_data = d["grid"]
        rows, cols = d["grid_rows"], d["grid_cols"]

        available_h = layout.content_height - 30
        cell_size   = min(
            layout.content_width  * 0.85 / cols,
            available_h * 0.85 / rows,
            60.0,
        )
        grid_w = cell_size * cols
        grid_h = cell_size * rows
        gx = layout.content_x + (layout.content_width - grid_w) / 2
        gy = layout.content_y + (available_h - grid_h) / 2

        for r in range(rows):
            for c in range(cols):
                cx = gx + c * cell_size
                cy = gy + (rows - 1 - r) * cell_size
                shape = grid_data[r][c]

                # Cell background
                canvas.setFillColor(white)
                canvas.rect(cx, cy, cell_size, cell_size, stroke=1, fill=1)
                canvas.setStrokeColor(_CELL_BORDER_COLOR)
                canvas.setLineWidth(0.3)

                # Draw shape centred in cell
                self._draw_shape(canvas, shape,
                                 cx + cell_size / 2, cy + cell_size / 2,
                                 cell_size * 0.38)

    def _draw_shape(self, canvas: Canvas, shape: str, cx: float, cy: float, r: float) -> None:
        """Draw a named shape centred at (cx, cy) with approximate radius r."""
        filled = "filled" in shape

        if "circle" in shape:
            canvas.setFillColor(black if filled else white)
            canvas.setStrokeColor(black)
            canvas.setLineWidth(1.2)
            canvas.circle(cx, cy, r, stroke=1, fill=1 if filled else 0)

        elif "square" in shape:
            canvas.setFillColor(black if filled else white)
            canvas.setStrokeColor(black)
            canvas.setLineWidth(1.2)
            canvas.rect(cx - r, cy - r, 2*r, 2*r, stroke=1, fill=1 if filled else 0)

        elif "triangle" in shape:
            p = canvas.beginPath()
            p.moveTo(cx, cy + r)
            p.lineTo(cx - r, cy - r)
            p.lineTo(cx + r, cy - r)
            p.close()
            canvas.setFillColor(black if filled else white)
            canvas.setStrokeColor(black)
            canvas.setLineWidth(1.2)
            canvas.drawPath(p, stroke=1, fill=1 if filled else 0)

        elif "diamond" in shape:
            p = canvas.beginPath()
            p.moveTo(cx, cy + r)
            p.lineTo(cx + r, cy)
            p.lineTo(cx, cy - r)
            p.lineTo(cx - r, cy)
            p.close()
            canvas.setFillColor(black if filled else white)
            canvas.setStrokeColor(black)
            canvas.setLineWidth(1.2)
            canvas.drawPath(p, stroke=1, fill=1 if filled else 0)

        elif "star" in shape:
            self._draw_star(canvas, cx, cy, r, filled)

        elif "cross" in shape:
            t = r * 0.3
            canvas.setFillColor(black)
            canvas.rect(cx - t, cy - r, 2*t, 2*r, stroke=0, fill=1)
            canvas.rect(cx - r, cy - t, 2*r, 2*t, stroke=0, fill=1)

    def _draw_star(self, canvas: Canvas, cx: float, cy: float, r: float, filled: bool) -> None:
        points = 5
        inner_r = r * 0.4
        path = canvas.beginPath()
        for i in range(points * 2):
            angle = math.pi / 2 + i * math.pi / points
            radius = r if i % 2 == 0 else inner_r
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)
            if i == 0:
                path.moveTo(px, py)
            else:
                path.lineTo(px, py)
        path.close()
        canvas.setFillColor(black if filled else white)
        canvas.setStrokeColor(black)
        canvas.setLineWidth(1.0)
        canvas.drawPath(path, stroke=1, fill=1 if filled else 0)

    # ======================================================================
    # Escape Room
    # ======================================================================

    def _render_escape_room_page(self, canvas: Canvas, layout: PageLayout,
                                  record: PuzzleRecord) -> None:
        self._draw_puzzle_header(canvas, layout, record)
        self._draw_footer(canvas, layout)

        d = record.puzzle_data
        intro = d.get("intro", "")
        steps = d["steps"]
        final_instruction = d.get("final_instruction", "Enter the final code to escape!")

        x = layout.content_x
        w = layout.content_width
        y = layout.content_y + layout.content_height - 20

        # Intro text
        if intro:
            canvas.setFont("Helvetica-Oblique", 9)
            canvas.setFillColor(_ACCENT)
            intro_lines = self._wrap_text(canvas, intro, "Helvetica-Oblique", 9, w)
            for line in intro_lines[:3]:
                canvas.drawString(x, y, line)
                y -= 13
            y -= 8

        # Steps
        step_h = min((y - layout.content_y - 40) / max(len(steps), 1), 100)
        for i, step in enumerate(steps):
            if y - step_h < layout.content_y:
                break

            # Step box
            by = y - step_h + 4
            canvas.setFillColor(HexColor("#ECF0F1"))
            canvas.roundRect(x, by, w, step_h - 6, 4, stroke=1, fill=1)

            # Label
            canvas.setFont("Helvetica-Bold", 9)
            canvas.setFillColor(_ACCENT)
            canvas.drawString(x + 8, y - 16, step.get("label", f"Step {i+1}"))

            # Clue text
            clue_lines = self._wrap_text(
                canvas, step["clue"], "Helvetica", 8, w - 16)
            for j, line in enumerate(clue_lines[:4]):
                canvas.setFont("Helvetica", 8)
                canvas.setFillColor(black)
                canvas.drawString(x + 8, y - 30 - j * 11, line)

            # Answer blank
            ans_y = by + 8
            canvas.setFont("Helvetica-Bold", 8)
            canvas.setFillColor(_DARK_GREY)
            canvas.drawString(x + 8, ans_y, "Answer: ___________")

            y -= step_h + 2

        # Final code box
        if y > layout.content_y + 30:
            canvas.setFillColor(HexColor("#2C3E50"))
            canvas.roundRect(x, y - 32, w, 28, 4, stroke=0, fill=1)
            canvas.setFont("Helvetica-Bold", 10)
            canvas.setFillColor(white)
            canvas.drawCentredString(x + w / 2, y - 22, final_instruction)

    # ======================================================================
    # Answer key entries
    # ======================================================================

    def render_answer_key_page(
        self,
        canvas: Canvas,
        layout: PageLayout,
        records: List[PuzzleRecord],
        start_index: int = 0,
    ) -> int:
        """Render answer-key entries. Returns index of first un-rendered record."""
        self._draw_header(canvas, layout, "Answer Key")
        self._draw_footer(canvas, layout)

        x = layout.content_x
        y = layout.content_y + layout.content_height

        idx = start_index
        while idx < len(records):
            rec = records[idx]
            if rec.answer is None:
                idx += 1
                continue
            
            pt = rec.puzzle_type
            if pt in ("sudoku", "word_search", "maze", "picture_puzzle"):
                cols = 3
            elif pt in ("logic_grid", "matching", "pattern"):
                cols = 2
            else:
                cols = 1
                
            cell_w = layout.content_width / cols
            
            row_entries = []
            max_h = 0
            
            for col in range(cols):
                if idx + col < len(records) and records[idx + col].puzzle_type == pt:
                    crec = records[idx + col]
                    if crec.answer is None:
                        continue
                    req_h = self._measure_answer_key_entry(canvas, cell_w, crec)
                    row_entries.append((crec, req_h))
                    max_h = max(max_h, req_h)
                else:
                    break
                    
            if not row_entries:
                idx += 1
                continue
                
            if y - max_h < layout.content_y:
                if y == layout.content_y + layout.content_height:
                    # Page is empty but it STILL doesn't fit. Force shrink or clip?
                    # Let's just draw it anyway to prevent infinite loops, but warn.
                    pass
                else:
                    return idx # Move to next page
                    
            for col, (crec, creq_h) in enumerate(row_entries):
                cx = x + col * cell_w
                bottom = y - max_h
                self._draw_answer_key_entry(canvas, cx, bottom, cell_w, max_h, crec)
                
            idx += len(row_entries)
            y -= (max_h + 10) # 10pt spacing between rows

        return len(records)

    def _measure_answer_key_entry(self, canvas: Canvas, w: float, record: PuzzleRecord) -> float:
        """Return the required height for this answer entry."""
        pt = record.puzzle_type
        padding = 4
        label_h = 10
        min_h = label_h + 2 * padding
        
        # Title always measured (handles wrapping if we wrap titles, but let's keep titles short/1-line if possible)
        # We will wrap titles to max 2 lines if needed.
        title = f"#{record.page_number} {record.title}"
        title_lines = self._wrap_text(canvas, title, "Helvetica-Bold", 7, w - 2*padding)
        title_h = len(title_lines) * 9 + 2
        
        if pt in ("sudoku", "word_search", "maze", "picture_puzzle"):
            # These are drawn as squares + label
            return w + title_h + padding
            
        elif pt == "logic_grid":
            sol = record.answer.answer_data
            h = title_h + padding
            for person, cats in sol.items():
                line = f"{person}: {', '.join(cats.values())}"
                lines = self._wrap_text(canvas, line, "Helvetica", 7, w - 2*padding)
                h += len(lines) * 9
            return h + padding

        elif pt == "matching":
            pairs = record.answer.answer_data.get("pairs", [])
            h = title_h + padding
            for a, b in pairs:
                line = f"{a} → {b}"
                lines = self._wrap_text(canvas, line, "Helvetica", 7, w - 2*padding)
                h += len(lines) * 9
            return h + padding
            
        elif pt == "pattern":
            seqs = record.answer.answer_data.get("sequences", [])
            h = title_h + padding
            for seq in seqs:
                line = f"{seq['display']} (Ans: {', '.join(seq['answers'])})"
                lines = self._wrap_text(canvas, line, "Helvetica", 7, w - 2*padding)
                h += len(lines) * 9
            return h + padding
            
        elif pt == "code_breaker":
            decoded = record.answer.answer_data.get("decoded", "")
            h = title_h + padding
            lines = self._wrap_text(canvas, f"Decoded: {decoded}", "Helvetica", 7, w - 2*padding)
            h += len(lines) * 9
            return h + padding
            
        elif pt == "critical_thinking":
            ans = record.answer.answer_data.get("answer", "")
            q = record.puzzle_data.get("question", "")
            h = title_h + padding
            lines_q = self._wrap_text(canvas, f"Q: {q}", "Helvetica-Oblique", 7, w - 2*padding)
            lines_a = self._wrap_text(canvas, f"A: {ans}", "Helvetica", 7, w - 2*padding)
            h += len(lines_q) * 9 + len(lines_a) * 9 + 4
            return h + padding
            
        elif pt == "escape_room":
            steps = record.answer.answer_data.get("steps", [])
            final = record.answer.answer_data.get("final_code", "")
            h = title_h + padding
            for i, step in enumerate(steps):
                line = f"Step {i+1}: {step['answer']}"
                lines = self._wrap_text(canvas, line, "Helvetica", 7, w - 2*padding)
                h += len(lines) * 9
            lines_f = self._wrap_text(canvas, f"Final: {final}", "Helvetica-Bold", 7, w - 2*padding)
            h += len(lines_f) * 9 + 4
            return h + padding

        else:
            return 50 # Default fallback

    def _draw_answer_key_entry(self, canvas: Canvas, x: float, y: float, w: float, h: float, record: PuzzleRecord) -> None:
        """Draw the answer key entry bounded by x, y, w, h."""
        pt = record.puzzle_type
        padding = 4
        
        # Border
        canvas.setStrokeColor(_MID_GREY)
        canvas.setLineWidth(0.5)
        canvas.rect(x+1, y+1, w-2, h-2, stroke=1, fill=0)
        
        # Title
        canvas.setFont("Helvetica-Bold", 7)
        canvas.setFillColor(_ACCENT)
        title = f"#{record.page_number} {record.title}"
        title_lines = self._wrap_text(canvas, title, "Helvetica-Bold", 7, w - 2*padding)
        ty = y + h - padding - 7
        for line in title_lines:
            canvas.drawString(x + padding, ty, line)
            ty -= 9
            
        ty -= 2 # Extra spacing after title

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(black)

        if pt == "sudoku":
            self._draw_mini_sudoku_answer(canvas, record, x, y, w, ty - y + padding)
        elif pt == "word_search":
            self._draw_mini_word_search_answer(canvas, record, x, y, w, ty - y + padding)
        elif pt == "maze":
            self._draw_mini_maze_answer(canvas, record, x, y, w, ty - y + padding)
        elif pt == "picture_puzzle":
            self._draw_mini_picture_puzzle_answer(canvas, record, x, y, w, ty - y + padding)
        elif pt == "logic_grid":
            sol = record.answer.answer_data
            for person, cats in sol.items():
                line = f"{person}: {', '.join(cats.values())}"
                lines = self._wrap_text(canvas, line, "Helvetica", 7, w - 2*padding)
                for l in lines:
                    canvas.drawString(x + padding, ty, l)
                    ty -= 9
        elif pt == "matching":
            pairs = record.answer.answer_data.get("pairs", [])
            for a, b in pairs:
                line = f"{a} → {b}"
                lines = self._wrap_text(canvas, line, "Helvetica", 7, w - 2*padding)
                for l in lines:
                    canvas.drawString(x + padding, ty, l)
                    ty -= 9
        elif pt == "pattern":
            seqs = record.answer.answer_data.get("sequences", [])
            for seq in seqs:
                line = f"{seq['display']} (Ans: {', '.join(seq['answers'])})"
                lines = self._wrap_text(canvas, line, "Helvetica", 7, w - 2*padding)
                for l in lines:
                    canvas.drawString(x + padding, ty, l)
                    ty -= 9
        elif pt == "code_breaker":
            decoded = record.answer.answer_data.get("decoded", "")
            lines = self._wrap_text(canvas, f"Decoded: {decoded}", "Helvetica", 7, w - 2*padding)
            for l in lines:
                canvas.drawString(x + padding, ty, l)
                ty -= 9
        elif pt == "critical_thinking":
            ans = record.answer.answer_data.get("answer", "")
            q = record.puzzle_data.get("question", "")
            lines_q = self._wrap_text(canvas, f"Q: {q}", "Helvetica-Oblique", 7, w - 2*padding)
            canvas.setFont("Helvetica-Oblique", 7)
            for l in lines_q:
                canvas.drawString(x + padding, ty, l)
                ty -= 9
            ty -= 2
            canvas.setFont("Helvetica", 7)
            lines_a = self._wrap_text(canvas, f"A: {ans}", "Helvetica", 7, w - 2*padding)
            for l in lines_a:
                canvas.drawString(x + padding, ty, l)
                ty -= 9
        elif pt == "escape_room":
            steps = record.answer.answer_data.get("steps", [])
            final = record.answer.answer_data.get("final_code", "")
            for i, step in enumerate(steps):
                line = f"Step {i+1}: {step['answer']}"
                lines = self._wrap_text(canvas, line, "Helvetica", 7, w - 2*padding)
                for l in lines:
                    canvas.drawString(x + padding, ty, l)
                    ty -= 9
            ty -= 2
            canvas.setFont("Helvetica-Bold", 7)
            lines_f = self._wrap_text(canvas, f"Final: {final}", "Helvetica-Bold", 7, w - 2*padding)
            for l in lines_f:
                canvas.drawString(x + padding, ty, l)
                ty -= 9
        else:
            canvas.drawString(x + padding, ty, "Unsupported type")

    def _draw_mini_sudoku_answer(self, canvas: Canvas, record: PuzzleRecord, x: float, y: float, w: float, h: float) -> None:
        grid = record.answer.answer_data
        if isinstance(grid, dict) and "grid" in grid:
            grid = grid["grid"]
        padding = 4
        cell_s = min((w - 2*padding)/9, (h - 2*padding)/9)
        gx = x + padding + (w - 2*padding - cell_s*9)/2
        gy = y + padding + (h - 2*padding - cell_s*9)/2
        font_s = max(3, cell_s * 0.7)
        
        canvas.setStrokeColor(black)
        for r in range(10):
            canvas.setLineWidth(1.0 if r % 3 == 0 else 0.25)
            canvas.line(gx, gy + r*cell_s, gx + 9*cell_s, gy + r*cell_s)
            canvas.line(gx + r*cell_s, gy, gx + r*cell_s, gy + 9*cell_s)
            
        canvas.setFillColor(black)
        canvas.setFont("Helvetica", font_s)
        for r in range(9):
            for c in range(9):
                val = grid[r][c]
                cx = gx + c * cell_s + cell_s / 2
                cy = gy + (8 - r) * cell_s + cell_s / 2 - font_s * 0.35
                canvas.drawCentredString(cx, cy, str(val))

    def _draw_mini_word_search_answer(self, canvas: Canvas, record: PuzzleRecord, x: float, y: float, w: float, h: float) -> None:
        grid = record.puzzle_data["grid"]
        ans = record.answer.answer_data.get("word_locations", {})
        if not ans:
            ans = record.answer.answer_data.get("words", {})
        rows, cols = len(grid), len(grid[0])
        padding = 4
        cell_s = min((w - 2*padding)/cols, (h - 2*padding)/rows)
        gx = x + padding + (w - 2*padding - cell_s*cols)/2
        gy = y + padding + (h - 2*padding - cell_s*rows)/2
        font_s = max(3, cell_s * 0.6)
        
        # Build set of solution cells
        sol_cells = set()
        for word, locs in ans.items():
            for loc in locs:
                sol_cells.add(tuple(loc))
                
        canvas.setStrokeColor(_MID_GREY)
        canvas.setLineWidth(0.25)
        for r in range(rows):
            for c in range(cols):
                is_sol = (r, c) in sol_cells
                cx = gx + c * cell_s
                cy = gy + (rows - 1 - r) * cell_s
                
                canvas.setFillColor(HexColor("#EEEEEE") if is_sol else white)
                canvas.rect(cx, cy, cell_s, cell_s, stroke=1, fill=1)
                
                if is_sol:
                    canvas.setFillColor(black)
                    canvas.setFont("Helvetica-Bold", font_s)
                else:
                    canvas.setFillColor(_MID_GREY)
                    canvas.setFont("Helvetica", font_s)
                    
                canvas.drawCentredString(cx + cell_s/2, cy + cell_s/2 - font_s*0.35, grid[r][c])

    def _draw_mini_maze_answer(self, canvas: Canvas, record: PuzzleRecord, x: float, y: float, w: float, h: float) -> None:
        walls = record.puzzle_data["walls"]
        path = record.answer.answer_data.get("path", [])
        if not path:
            path = record.puzzle_data.get("solution", [])
        rows, cols = len(walls), len(walls[0])
        padding = 4
        cell_s = min((w - 2*padding)/cols, (h - 2*padding)/rows)
        gx = x + padding + (w - 2*padding - cell_s*cols)/2
        gy = y + padding + (h - 2*padding - cell_s*rows)/2
        
        canvas.setStrokeColor(black)
        canvas.setLineWidth(0.5)
        for r in range(rows):
            for c in range(cols):
                cx = gx + c * cell_s
                cy = gy + (rows - 1 - r) * cell_s
                cell_walls = walls[r][c]
                if cell_walls.get("N"): canvas.line(cx, cy + cell_s, cx + cell_s, cy + cell_s)
                if cell_walls.get("S"): canvas.line(cx, cy, cx + cell_s, cy)
                if cell_walls.get("E"): canvas.line(cx + cell_s, cy, cx + cell_s, cy + cell_s)
                if cell_walls.get("W"): canvas.line(cx, cy, cx, cy + cell_s)
                
        if path:
            canvas.setStrokeColor(_ACCENT)
            canvas.setLineWidth(1.0)
            p = canvas.beginPath()
            r0, c0 = path[0]
            p.moveTo(gx + c0*cell_s + cell_s/2, gy + (rows - 1 - r0)*cell_s + cell_s/2)
            for r, c in path[1:]:
                p.lineTo(gx + c*cell_s + cell_s/2, gy + (rows - 1 - r)*cell_s + cell_s/2)
            canvas.drawPath(p, stroke=1, fill=0)

    def _draw_mini_picture_puzzle_answer(self, canvas: Canvas, record: PuzzleRecord, x: float, y: float, w: float, h: float) -> None:
        grid = record.puzzle_data["grid"]
        rows, cols = record.puzzle_data["grid_rows"], record.puzzle_data["grid_cols"]
        odd_r, odd_c = record.answer.answer_data["odd_row"], record.answer.answer_data["odd_col"]
        
        padding = 4
        cell_s = min((w - 2*padding) / cols, (h - 2*padding) / rows)
        gx = x + padding + (w - 2*padding - cell_s*cols)/2
        gy = y + padding + (h - 2*padding - cell_s*rows)/2
        
        font_s = max(3, cell_s * 0.55)
        
        for r in range(rows):
            for c in range(cols):
                cx = gx + c * cell_s
                cy = gy + (rows-1-r) * cell_s
                is_odd = (r == odd_r and c == odd_c)
                canvas.setFillColor(HexColor("#FFCDD2") if is_odd else white)
                canvas.rect(cx, cy, cell_s, cell_s, stroke=1, fill=1)
                
                canvas.setFillColor(black)
                canvas.setFont("Helvetica", font_s)
                canvas.drawCentredString(cx + cell_s/2, cy + cell_s/2 - font_s*0.35, grid[r][c])

    # ======================================================================
    # Title / Intro pages
    # ======================================================================

    def render_title_page(self, canvas: Canvas, layout: PageLayout) -> None:
        cx = layout.dims.trim_width / 2
        mid_y = layout.content_y + layout.content_height / 2
        canvas.setFont("Helvetica-Bold", 28)
        canvas.setFillColor(black)
        canvas.drawCentredString(cx, mid_y + 40, self.settings.title)
        if self.settings.subtitle:
            canvas.setFont("Helvetica", 16)
            canvas.drawCentredString(cx, mid_y + 10, self.settings.subtitle)
        canvas.setFont("Helvetica-Oblique", 12)
        canvas.drawCentredString(cx, mid_y - 20, f"by {self.settings.author}")
        canvas.setStrokeColor(HexColor("#CCCCCC"))
        canvas.setLineWidth(0.5)
        canvas.line(layout.content_x + 40, mid_y + 32,
                    layout.content_x + layout.content_width - 40, mid_y + 32)
        self._draw_footer(canvas, layout)

    def render_intro_page(self, canvas: Canvas, layout: PageLayout) -> None:
        self._draw_header(canvas, layout, "Introduction")
        self._draw_footer(canvas, layout)
        x = layout.content_x
        y = layout.content_y + layout.content_height - 20
        canvas.setFont("Helvetica-Bold", 13)
        canvas.setFillColor(black)
        canvas.drawString(x, y, "Welcome to Your Puzzle Book!")
        y -= 20
        lines = [
            "This book contains a variety of brain-challenging puzzles designed to",
            "entertain, educate, and sharpen your thinking skills.",
            "",
            "Puzzle Types Included:",
            "  • Sudoku — fill the 9×9 grid with digits 1–9, no repeats.",
            "  • Word Search — find hidden words in a letter grid.",
            "  • Maze — navigate from START to FINISH.",
            "  • Logic Grid — use clues to deduce who has what.",
            "  • Code Breaker — decode a secret message.",
            "  • Matching — connect each item to its correct pair.",
            "  • Pattern — find the missing number in each sequence.",
            "  • Think It Through — logical riddles and brain teasers.",
            "  • Spot the Difference — find the odd shape in the grid.",
            "  • Escape Room — solve a chain of clues to escape!",
            "",
            "Tips:",
            "  • Work through each puzzle at your own pace.",
            "  • Use the answer key at the back if you get stuck.",
            "  • Challenge yourself to beat your previous best time!",
        ]
        canvas.setFont("Helvetica", 10)
        for line in lines:
            if y < layout.content_y:
                break
            canvas.drawString(x, y, line)
            y -= 14

    # ======================================================================
    # Shared header / footer / instruction drawing
    # ======================================================================

    def _draw_puzzle_header(self, canvas: Canvas, layout: PageLayout,
                             record: PuzzleRecord) -> None:
        self._draw_header(canvas, layout, record.title)

    def _draw_header(self, canvas: Canvas, layout: PageLayout,
                     section_title: str = "") -> None:
        if layout.header_height <= 0:
            return
        y = layout.header_y + 2
        canvas.setFont("Helvetica", _HEADER_FONT_SIZE)
        canvas.setFillColor(HexColor("#444444"))
        left_x  = layout.safe_area_x
        right_x = layout.safe_area_x + layout.safe_area_width
        if layout.is_recto:
            canvas.drawString(left_x, y, self.settings.title)
            if section_title:
                canvas.drawRightString(right_x, y, section_title)
        else:
            if section_title:
                canvas.drawString(left_x, y, section_title)
            canvas.drawRightString(right_x, y, self.settings.title)
        canvas.setStrokeColor(HexColor("#CCCCCC"))
        canvas.setLineWidth(0.4)
        canvas.line(left_x, layout.header_y - 1, right_x, layout.header_y - 1)

    def _draw_footer(self, canvas: Canvas, layout: PageLayout) -> None:
        if layout.footer_height <= 0 or not self.settings.page_numbering:
            return
        if layout.page_number is None:
            return
        y    = layout.footer_y + 2
        mid  = layout.safe_area_x + layout.safe_area_width / 2
        lx   = layout.safe_area_x
        rx   = layout.safe_area_x + layout.safe_area_width
        canvas.setFont("Helvetica", _FOOTER_FONT_SIZE)
        canvas.setFillColor(HexColor("#666666"))
        canvas.drawCentredString(mid, y, str(layout.page_number))
        canvas.setStrokeColor(HexColor("#CCCCCC"))
        canvas.setLineWidth(0.4)
        canvas.line(lx, layout.footer_y + layout.footer_height - 1,
                    rx, layout.footer_y + layout.footer_height - 1)

    def _draw_instructions(self, canvas: Canvas, layout: PageLayout, text: str) -> None:
        if not text:
            return
        x = layout.content_x
        y = layout.content_y + layout.content_height - 18
        canvas.setFont("Helvetica-Oblique", _INSTRUCTION_FONT_SIZE)
        canvas.setFillColor(HexColor("#333333"))
        max_w = layout.content_width
        words = text.split()
        line = ""
        for word in words:
            test = (line + " " + word).strip()
            if canvas.stringWidth(test, "Helvetica-Oblique", _INSTRUCTION_FONT_SIZE) < max_w:
                line = test
            else:
                canvas.drawString(x, y, line)
                y -= 12
                line = word
        if line:
            canvas.drawString(x, y, line)

    # ======================================================================
    # Sudoku grid (Phase 2, kept here)
    # ======================================================================

    def _draw_sudoku_grid(self, canvas: Canvas, layout: PageLayout,
                          record: PuzzleRecord) -> None:
        givens = record.puzzle_data["givens"]
        available_h = layout.content_height - 30
        available_w = layout.content_width
        grid_size   = min(available_w * 0.92, available_h * 0.92)
        cell_size   = grid_size / 9
        grid_x      = layout.content_x + (layout.content_width - grid_size) / 2
        grid_y      = layout.content_y + (available_h - grid_size) / 2

        if not layout.contains_rect(grid_x, grid_y, grid_size, grid_size):
            raise ValueError("Sudoku grid overflows safe area.")

        for row in range(9):
            for col in range(9):
                cx = grid_x + col * cell_size
                cy = grid_y + (8 - row) * cell_size
                val = givens[row][col]
                canvas.setFillColor(_GIVEN_BG if val != 0 else white)
                canvas.rect(cx, cy, cell_size, cell_size, stroke=0, fill=1)
                if val != 0:
                    canvas.setFillColor(black)
                    canvas.setFont("Helvetica-Bold", _GIVEN_FONT_SIZE)
                    canvas.drawCentredString(
                        cx + cell_size / 2,
                        cy + cell_size / 2 - _GIVEN_FONT_SIZE * 0.35,
                        str(val)
                    )

        for i in range(10):
            is_box = (i % 3 == 0)
            lw = _GRID_LINE_THICK if is_box else _GRID_LINE_THIN
            color = _BOX_BORDER_COLOR if is_box else _CELL_BORDER_COLOR
            canvas.setLineWidth(lw)
            canvas.setStrokeColor(color)
            canvas.line(grid_x, grid_y + i*cell_size, grid_x + grid_size, grid_y + i*cell_size)
            canvas.line(grid_x + i*cell_size, grid_y, grid_x + i*cell_size, grid_y + grid_size)

    def _render_placeholder(self, canvas: Canvas, layout: PageLayout,
                             record: PuzzleRecord) -> None:
        canvas.setFont("Helvetica", 12)
        canvas.setFillColor(black)
        canvas.drawString(layout.content_x, layout.content_y + layout.content_height/2,
                          f"[{record.puzzle_type}] — renderer not yet implemented")

    # ======================================================================
    # Utility
    # ======================================================================

    @staticmethod
    def _wrap_text(canvas: Canvas, text: str, font: str, size: float, max_w: float) -> List[str]:
        words = text.replace("\n", " \n ").split()
        lines, line = [], ""
        for word in words:
            if word == "\n":
                lines.append(line)
                line = ""
                continue
                
            test = (line + " " + word).strip()
            if canvas.stringWidth(test, font, size) < max_w:
                line = test
            else:
                # The word alone might be longer than max_w
                if line:
                    lines.append(line)
                    line = ""
                
                # If word itself is too long, we must break it forcibly
                if canvas.stringWidth(word, font, size) >= max_w:
                    sub_word = ""
                    for ch in word:
                        if canvas.stringWidth(sub_word + ch, font, size) < max_w:
                            sub_word += ch
                        else:
                            lines.append(sub_word)
                            sub_word = ch
                    line = sub_word
                else:
                    line = word
                    
        if line:
            lines.append(line)
        return [l for l in lines if l]


# ---------------------------------------------------------------------------
# Helper: extract human-readable answer for text blocks
# ---------------------------------------------------------------------------

def _extract_answer_text(puzzle_type: str, answer_data: dict) -> str:
    if puzzle_type == "code_breaker":
        return f"Decoded: {answer_data.get('decoded', '')}"
    if puzzle_type == "matching":
        pairs = answer_data.get("pairs", [])
        return " | ".join(f"{a}→{b}" for a, b in pairs[:4])
    if puzzle_type == "pattern":
        seqs = answer_data.get("sequences", [])
        parts = []
        for s in seqs[:3]:
            ans = ", ".join(str(v) for v in s.get("answers", {}).values())
            parts.append(ans)
        return "  ".join(parts)
    if puzzle_type == "critical_thinking":
        return f"Answer: {answer_data.get('answer', '')}"
    if puzzle_type == "picture_puzzle":
        return f"Odd one: row {answer_data.get('odd_row',0)+1}, col {answer_data.get('odd_col',0)+1}"
    if puzzle_type == "escape_room":
        return f"Final code: {answer_data.get('final_code', '')}"
    if puzzle_type == "logic_grid":
        sol = answer_data.get("solution", {})
        return "  ".join(f"{p}:{list(v.values())}" for p, v in list(sol.items())[:2])
    return str(answer_data)[:60]
