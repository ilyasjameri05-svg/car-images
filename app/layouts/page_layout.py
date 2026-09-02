"""
Deterministic page layout engine.

Given BookSettings and a page number, computes every positional value
needed to render that page — safe area, header, footer, content area.

No element is allowed to exceed the safe area; the layout engine enforces
this at computation time so the PDF renderer can trust the returned values.
"""
from __future__ import annotations

from app.models.book import BookSettings
from app.models.layout import PageDimensions, PageMargins, PageLayout, POINTS_PER_INCH
from app.layouts.dimensions import get_page_dimensions


# Default header/footer heights (points)
_HEADER_HEIGHT_PT = 14.0   # 14pt ≈ small line of text
_FOOTER_HEIGHT_PT = 14.0
_HEADER_GAP_PT = 6.0       # gap between header and content
_FOOTER_GAP_PT = 6.0


def compute_margins(settings: BookSettings, dims: PageDimensions) -> PageMargins:
    """Convert margin settings from inches to points."""
    return PageMargins(
        top=settings.margin_top_in * POINTS_PER_INCH,
        bottom=settings.margin_bottom_in * POINTS_PER_INCH,
        inner=settings.margin_inner_in * POINTS_PER_INCH,
        outer=settings.margin_outer_in * POINTS_PER_INCH,
    )


def compute_page_layout(
    settings: BookSettings,
    page_number: int,
    dims: PageDimensions | None = None,
) -> PageLayout:
    """
    Compute the complete layout for one page.

    Parameters
    ----------
    settings:    BookSettings driving the layout.
    page_number: Physical page number (1-based). Odd = recto (right-hand).
    dims:        Pre-computed PageDimensions; derived from settings if None.

    Returns
    -------
    PageLayout with all coordinate fields populated in points.
    """
    if dims is None:
        dims = get_page_dimensions(settings)

    margins = compute_margins(settings, dims)
    is_recto = (page_number % 2 == 1)

    # In a printed book the inner margin is on the spine side.
    # Recto pages (right-hand) have the spine on the left → inner = left margin.
    # Verso pages (left-hand)  have the spine on the right → inner = right margin.
    if is_recto:
        left_margin = margins.inner
        right_margin = margins.outer
    else:
        left_margin = margins.outer
        right_margin = margins.inner

    # --- Safe area ---
    # The safe area is the rectangle excluding all margins.
    # Coordinates in ReportLab: (0,0) = bottom-left, y increases upward.
    safe_x = left_margin
    safe_y = margins.bottom
    safe_w = dims.trim_width - left_margin - right_margin
    safe_h = dims.trim_height - margins.top - margins.bottom

    # Sanity check: safe area must be positive
    if safe_w <= 0 or safe_h <= 0:
        raise ValueError(
            f"Margins are too large for the page size. "
            f"safe_w={safe_w:.1f}pt, safe_h={safe_h:.1f}pt"
        )

    # --- Header ---
    header_h = _HEADER_HEIGHT_PT if settings.page_numbering else 0.0
    # Header sits at the TOP of the safe area
    header_y = safe_y + safe_h - header_h  # bottom-y of header band

    # --- Footer ---
    footer_h = _FOOTER_HEIGHT_PT if settings.page_numbering else 0.0
    footer_y = safe_y  # bottom of footer = bottom of safe area

    # --- Content area (between footer and header) ---
    content_x = safe_x
    content_y = safe_y + footer_h + (_FOOTER_GAP_PT if footer_h else 0)
    content_w = safe_w
    content_h = (
        safe_h
        - header_h - (_HEADER_GAP_PT if header_h else 0)
        - footer_h - (_FOOTER_GAP_PT if footer_h else 0)
    )

    if content_h <= 0:
        raise ValueError(
            f"Content height is non-positive ({content_h:.1f}pt). "
            "Reduce margins or header/footer size."
        )

    layout = PageLayout(
        dims=dims,
        margins=margins,
        page_number=page_number,
        is_recto=is_recto,
        safe_area_x=safe_x,
        safe_area_y=safe_y,
        safe_area_width=safe_w,
        safe_area_height=safe_h,
        header_height=header_h,
        footer_height=footer_h,
        header_y=header_y,
        footer_y=footer_y,
        content_x=content_x,
        content_y=content_y,
        content_width=content_w,
        content_height=content_h,
    )

    return layout
