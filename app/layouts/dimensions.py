"""
KDP page dimension catalog.

All common Amazon KDP trim sizes are defined here in points.
No other file should hard-code page sizes.

1 inch = 72 points (PDF / ReportLab standard).
"""
from __future__ import annotations

from app.models.book import BookSettings, Orientation, TrimSize
from app.models.layout import PageDimensions, POINTS_PER_INCH


# ---------------------------------------------------------------------------
# Trim-size catalog  (width_in, height_in)  — portrait orientation
# ---------------------------------------------------------------------------

_TRIM_CATALOG: dict[TrimSize, tuple[float, float]] = {
    TrimSize.SIX_BY_NINE:               (6.0,  9.0),
    TrimSize.EIGHT_BY_TEN:              (8.0, 10.0),
    TrimSize.EIGHT_HALF_BY_ELEVEN:      (8.5, 11.0),
    TrimSize.EIGHT_HALF_BY_EIGHT_HALF:  (8.5,  8.5),
    TrimSize.FIVE_BY_EIGHT:             (5.0,  8.0),
    TrimSize.FIVE_HALF_BY_EIGHT_HALF:   (5.5,  8.5),
    TrimSize.SEVEN_BY_TEN:              (7.0, 10.0),
}


def get_page_dimensions(settings: BookSettings) -> PageDimensions:
    """
    Compute final PageDimensions from BookSettings.

    Handles:
    - Standard KDP trim sizes
    - Custom dimensions
    - Portrait / Landscape orientation swap
    - Bleed on/off
    """
    if settings.trim_size == TrimSize.CUSTOM:
        w_in = settings.custom_width_in
        h_in = settings.custom_height_in
    else:
        w_in, h_in = _TRIM_CATALOG[settings.trim_size]

    # Apply orientation swap
    if settings.orientation == Orientation.LANDSCAPE:
        w_in, h_in = h_in, w_in

    # Convert to points
    trim_w = w_in * POINTS_PER_INCH
    trim_h = h_in * POINTS_PER_INCH

    # Apply bleed
    bleed_pt = 0.0
    if settings.bleed:
        bleed_pt = settings.bleed_amount_in * POINTS_PER_INCH

    full_w = trim_w + 2 * bleed_pt
    full_h = trim_h + 2 * bleed_pt

    return PageDimensions(
        width=full_w,
        height=full_h,
        trim_width=trim_w,
        trim_height=trim_h,
        bleed=bleed_pt,
        orientation=settings.orientation.value,
    )


def list_standard_sizes() -> list[dict]:
    """Return a list of all standard KDP sizes for UI display."""
    result = []
    for size, (w, h) in _TRIM_CATALOG.items():
        result.append({"id": size.value, "width_in": w, "height_in": h,
                       "label": f"{size.value} ({w}\" × {h}\")"})
    return result
