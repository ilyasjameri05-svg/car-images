"""
PDFRenderer — orchestrates the full book PDF using ReportLab.

Responsibilities:
- Create the ReportLab Canvas with EXACT physical page dimensions.
- Call the layout engine for each page.
- Delegate drawing to PageRenderer.
- Maintain correct page numbering and page order.
- Flush each page with canvas.showPage().
- Save the final PDF.

This module knows about book structure (which pages are included and in what
order) but knows nothing about individual puzzle types — that logic lives in
PageRenderer.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from reportlab.pdfgen.canvas import Canvas

from app.models.book import BookSettings
from app.models.layout import PageLayout
from app.models.puzzle import PuzzleRecord
from app.layouts.dimensions import get_page_dimensions
from app.layouts.page_layout import compute_page_layout
from app.pdf.page_renderer import PageRenderer


class PDFRenderer:
    """
    Renders a complete puzzle book PDF.

    Usage
    -----
    renderer = PDFRenderer(settings)
    renderer.render_book(puzzles, "output.pdf")
    """

    def __init__(self, settings: BookSettings) -> None:
        self.settings = settings
        self.dims = get_page_dimensions(settings)
        self.page_renderer = PageRenderer(settings)

    def render_book(
        self,
        puzzles: List[PuzzleRecord],
        output_path: str,
    ) -> None:
        """
        Generate the complete PDF book and save it to `output_path`.

        Page order:
        1. Cover (blank / title-only, if enabled)
        2. Title page (if enabled)
        3. Introduction (if enabled)
        4. Puzzle pages
        5. Answer key (if enabled)
        """
        output_path = str(Path(output_path).resolve())
        canvas = Canvas(
            output_path,
            pagesize=(self.dims.trim_width, self.dims.trim_height),
        )
        # Embed metadata
        canvas.setTitle(self.settings.title)
        canvas.setAuthor(self.settings.author)
        canvas.setSubject(self.settings.subtitle or "Puzzle Book")
        canvas.setCreator("KDP Puzzle Book Generator")

        page_num = 0

        # -- Cover page --
        if self.settings.include_cover:
            page_num += 1
            layout = compute_page_layout(self.settings, page_num, self.dims)
            self._render_cover(canvas, layout)
            canvas.showPage()

        # -- Title page --
        if self.settings.include_title_page:
            page_num += 1
            layout = compute_page_layout(self.settings, page_num, self.dims)
            self.page_renderer.render_title_page(canvas, layout)
            canvas.showPage()

        # -- Introduction --
        if self.settings.include_introduction:
            page_num += 1
            layout = compute_page_layout(self.settings, page_num, self.dims)
            self.page_renderer.render_intro_page(canvas, layout)
            canvas.showPage()

        # -- Puzzle pages --
        for i, record in enumerate(puzzles):
            page_num += 1
            record.page_number = page_num
            layout = compute_page_layout(self.settings, page_num, self.dims)
            self.page_renderer.render_puzzle_page(canvas, layout, record)
            canvas.showPage()


        # -- Answer key --
        if self.settings.include_answer_key and puzzles:
            idx = 0
            while idx < len(puzzles):
                page_num += 1
                layout = compute_page_layout(self.settings, page_num, self.dims)
                idx = self.page_renderer.render_answer_key_page(
                    canvas, layout, puzzles, start_index=idx
                )
                canvas.showPage()

        canvas.save()
        print(f"PDF saved: {output_path} ({page_num} pages)")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _render_cover(self, canvas: Canvas, layout: PageLayout) -> None:
        """Simple cover page — title centred with a border."""
        from reportlab.lib.colors import HexColor, black

        w = self.dims.trim_width
        h = self.dims.trim_height

        # Background
        canvas.setFillColor(HexColor("#1A1A2E"))
        canvas.rect(0, 0, w, h, stroke=0, fill=1)

        # Border
        margin = 18
        canvas.setStrokeColor(HexColor("#E0E0E0"))
        canvas.setLineWidth(1.0)
        canvas.rect(margin, margin, w - 2 * margin, h - 2 * margin,
                    stroke=1, fill=0)

        mid_x = w / 2
        mid_y = h / 2

        # Title
        canvas.setFillColor(HexColor("#FFFFFF"))
        canvas.setFont("Helvetica-Bold", 32)
        canvas.drawCentredString(mid_x, mid_y + 30, self.settings.title)

        # Subtitle
        if self.settings.subtitle:
            canvas.setFont("Helvetica", 16)
            canvas.setFillColor(HexColor("#AAAAAA"))
            canvas.drawCentredString(mid_x, mid_y - 5, self.settings.subtitle)

        # Author
        canvas.setFont("Helvetica-Oblique", 13)
        canvas.setFillColor(HexColor("#888888"))
        canvas.drawCentredString(mid_x, mid_y - 35, f"by {self.settings.author}")

        # Difficulty badge
        badge_w, badge_h = 90, 22
        badge_x = mid_x - badge_w / 2
        badge_y = mid_y - 75
        canvas.setFillColor(HexColor("#E94560"))
        canvas.roundRect(badge_x, badge_y, badge_w, badge_h, 4, stroke=0, fill=1)
        canvas.setFillColor(HexColor("#FFFFFF"))
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawCentredString(
            mid_x, badge_y + 7, "MIXED PUZZLES"
        )

    def _render_placeholder(
        self,
        canvas: Canvas,
        layout: PageLayout,
        record: PuzzleRecord,
    ) -> None:
        """Minimal placeholder for unsupported puzzle types."""
        from reportlab.lib.colors import black
        canvas.setFont("Helvetica", 12)
        canvas.setFillColor(black)
        canvas.drawString(
            layout.content_x,
            layout.content_y + layout.content_height / 2,
            f"[{record.puzzle_type}] — Not yet implemented",
        )
