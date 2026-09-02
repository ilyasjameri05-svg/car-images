"""
Layout data models: PageDimensions and PageLayout.

All measurements are stored internally in points (1 inch = 72 points).
This is the native unit of ReportLab and PDF coordinates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


POINTS_PER_INCH = 72.0


@dataclass(frozen=True)
class PageDimensions:
    """
    Physical dimensions of a single page in points.

    width and height are the FINAL rendered dimensions including bleed.
    trim_width and trim_height are the user-visible (trimmed) area.
    """
    width: float          # points — full page (may include bleed)
    height: float         # points — full page (may include bleed)
    trim_width: float     # points — trimmed area (no bleed)
    trim_height: float    # points — trimmed area (no bleed)
    bleed: float = 0.0    # points — bleed amount on each side
    orientation: str = "portrait"

    # Convenience properties

    @property
    def width_in(self) -> float:
        return self.width / POINTS_PER_INCH

    @property
    def height_in(self) -> float:
        return self.height / POINTS_PER_INCH

    @property
    def trim_width_in(self) -> float:
        return self.trim_width / POINTS_PER_INCH

    @property
    def trim_height_in(self) -> float:
        return self.trim_height / POINTS_PER_INCH

    def __str__(self) -> str:
        return (
            f"PageDimensions({self.trim_width_in:.3f}\" × {self.trim_height_in:.3f}\""
            f" | bleed={self.bleed / POINTS_PER_INCH:.3f}\" | {self.orientation})"
        )


@dataclass
class PageMargins:
    """Margins for one page in points."""
    top: float
    bottom: float
    inner: float   # gutter side (spine)
    outer: float   # outer edge

    @property
    def top_in(self) -> float: return self.top / POINTS_PER_INCH
    @property
    def bottom_in(self) -> float: return self.bottom / POINTS_PER_INCH
    @property
    def inner_in(self) -> float: return self.inner / POINTS_PER_INCH
    @property
    def outer_in(self) -> float: return self.outer / POINTS_PER_INCH


@dataclass
class PageLayout:
    """
    Fully computed layout for a single page.

    All coordinates use ReportLab's coordinate system:
      - Origin (0, 0) is at the BOTTOM-LEFT of the page.
      - y increases upward.

    The safe_area_* fields define the rectangle available for content,
    accounting for margins and bleed offset.
    """
    dims: PageDimensions
    margins: PageMargins
    page_number: Optional[int] = None
    is_recto: bool = True           # True = right-hand page (odd number)

    # Computed fields (set by layout engine)
    safe_area_x: float = field(default=0.0)
    safe_area_y: float = field(default=0.0)
    safe_area_width: float = field(default=0.0)
    safe_area_height: float = field(default=0.0)

    # Sub-areas within the safe area
    header_height: float = field(default=0.0)
    footer_height: float = field(default=0.0)
    header_y: float = field(default=0.0)
    footer_y: float = field(default=0.0)

    # Content area (safe area minus header and footer)
    content_x: float = field(default=0.0)
    content_y: float = field(default=0.0)
    content_width: float = field(default=0.0)
    content_height: float = field(default=0.0)

    @property
    def safe_area_x_in(self) -> float: return self.safe_area_x / POINTS_PER_INCH
    @property
    def safe_area_y_in(self) -> float: return self.safe_area_y / POINTS_PER_INCH
    @property
    def safe_area_width_in(self) -> float: return self.safe_area_width / POINTS_PER_INCH
    @property
    def safe_area_height_in(self) -> float: return self.safe_area_height / POINTS_PER_INCH
    @property
    def content_width_in(self) -> float: return self.content_width / POINTS_PER_INCH
    @property
    def content_height_in(self) -> float: return self.content_height / POINTS_PER_INCH

    def contains_rect(self, x: float, y: float, w: float, h: float) -> bool:
        """Return True if the rectangle (x,y,w,h) fits inside the safe area."""
        return (
            x >= self.safe_area_x
            and y >= self.safe_area_y
            and (x + w) <= (self.safe_area_x + self.safe_area_width)
            and (y + h) <= (self.safe_area_y + self.safe_area_height)
        )
