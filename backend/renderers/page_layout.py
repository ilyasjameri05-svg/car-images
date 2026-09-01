"""
Page Layout Engine — calculates zones for each page size with dynamic space optimization.

Handles safe margins, grid area, title area, color key area, decoration zones,
and page numbering. Protected puzzle area: decorations cannot enter.
"""
from dataclasses import dataclass, field
from backend.config import PAGE_SIZES, PageSize, Orientation


@dataclass
class LayoutZone:
    """A rectangular zone on the page (in points)."""
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2


@dataclass
class PageLayout:
    """Complete page layout with calculated zones."""
    page_width: float
    page_height: float
    title_zone: LayoutZone
    grid_zone: LayoutZone         # PROTECTED: decorations cannot enter
    color_key_zone: LayoutZone
    page_number_zone: LayoutZone
    decoration_zones: list[LayoutZone]  # Corners and edges for decorations
    margin_top: float
    margin_bottom: float
    margin_inside: float
    margin_outside: float
    cell_size: float              # Size of each grid cell in points
    grid_width: int               # Number of columns
    grid_height: int              # Number of rows
    color_key_cols: int = 2       # Calculated number of columns in color key
    readability_warning: str | None = None


def calculate_layout(
    page_size_key: str,
    orientation: str,
    grid_width: int,
    grid_height: int,
    has_title: bool = True,
    has_color_key: bool = True,
    color_count: int = 10,
) -> PageLayout:
    """Calculate the complete page layout for a given page size and grid.

    Optimizes available page area by calculating dynamic columns for the color key,
    maximizing the puzzle grid size within KDP safe margins.

    Args:
        page_size_key: Key from PAGE_SIZES (e.g. "kdp_8_5x11").
        orientation: "portrait" or "landscape".
        grid_width: Number of grid columns.
        grid_height: Number of grid rows.
        has_title: Whether to reserve space for a title.
        has_color_key: Whether to reserve space for a color key.
        color_count: Number of colors (affects color key height).

    Returns:
        PageLayout with all zones calculated.
    """
    page_size = PAGE_SIZES.get(page_size_key)
    if page_size is None:
        page_size = PAGE_SIZES["kdp_8_5x11"]

    # Apply orientation
    if orientation == "landscape":
        page_w = page_size.height_pt
        page_h = page_size.width_pt
    else:
        page_w = page_size.width_pt
        page_h = page_size.height_pt

    mt = page_size.margin_top_pt
    mb = page_size.margin_bottom_pt
    mi = page_size.margin_inside_pt
    mo = page_size.margin_outside_pt

    # Usable area
    usable_w = page_w - mi - mo
    usable_h = page_h - mt - mb

    # Title zone (top of usable area)
    title_h = 28.0 if has_title else 0.0
    title_zone = LayoutZone(mi, mt, usable_w, title_h)

    # Page number zone (bottom)
    page_num_h = 16.0
    page_number_zone = LayoutZone(mi, page_h - mb - page_num_h,
                                  usable_w, page_num_h)

    # Color key zone (below grid)
    # Dynamic columns: 2 columns for <= 8 colors, 3 columns for 9-14, 4 columns for 15+
    key_cols = 4 if color_count >= 15 else (3 if color_count >= 9 else 2)
    key_rows = (color_count + key_cols - 1) // key_cols
    key_h = max(26.0, key_rows * 14.0 + 8.0) if has_color_key else 0.0
    key_gap = 8.0 if has_color_key else 0.0

    # Grid zone — the remaining space between title and color key
    grid_top = mt + title_h + (6.0 if has_title else 0.0)
    grid_bottom_limit = page_h - mb - page_num_h - key_h - key_gap - 6.0
    available_grid_h = max(10.0, grid_bottom_limit - grid_top)
    available_grid_w = usable_w

    # Calculate cell size — must be equal width and height (square cells)
    cell_size_w = available_grid_w / grid_width
    cell_size_h = available_grid_h / grid_height
    cell_size = min(cell_size_w, cell_size_h)

    # Actual grid dimensions
    actual_grid_w = cell_size * grid_width
    actual_grid_h = cell_size * grid_height

    # Center the grid horizontally
    grid_x = mi + (usable_w - actual_grid_w) / 2
    grid_y = grid_top + (available_grid_h - actual_grid_h) / 2

    grid_zone = LayoutZone(grid_x, grid_y, actual_grid_w, actual_grid_h)

    # Color key zone positioned below grid
    color_key_zone = LayoutZone(
        grid_x, grid_zone.bottom + key_gap,
        actual_grid_w, key_h
    )

    # Readability warning for dense grids (cell size in points, 1pt = 0.3528mm)
    # 10pt = ~3.5mm; 7pt = ~2.5mm
    readability_warning = None
    if cell_size < 10.0:
        readability_warning = "High grid density: numbers may be difficult to read in print."

    # Decoration zones — corners and edges outside the protected grid area
    deco_zones = _calculate_decoration_zones(
        page_w, page_h, grid_zone, mt, mb, mi, mo
    )

    return PageLayout(
        page_width=page_w,
        page_height=page_h,
        title_zone=title_zone,
        grid_zone=grid_zone,
        color_key_zone=color_key_zone,
        page_number_zone=page_number_zone,
        decoration_zones=deco_zones,
        margin_top=mt,
        margin_bottom=mb,
        margin_inside=mi,
        margin_outside=mo,
        cell_size=cell_size,
        grid_width=grid_width,
        grid_height=grid_height,
        color_key_cols=key_cols,
        readability_warning=readability_warning,
    )


def _calculate_decoration_zones(
    page_w: float, page_h: float,
    grid_zone: LayoutZone,
    mt: float, mb: float, mi: float, mo: float,
) -> list[LayoutZone]:
    """Calculate decoration zones in the four corners around the grid."""
    zones = []
    margin = 4.0  # gap between decoration and grid

    # Top-left corner
    zones.append(LayoutZone(
        mi, mt,
        grid_zone.x - mi - margin,
        grid_zone.y - mt - margin,
    ))
    # Top-right corner
    zones.append(LayoutZone(
        grid_zone.right + margin, mt,
        page_w - mo - grid_zone.right - margin,
        grid_zone.y - mt - margin,
    ))
    # Bottom-left corner
    zones.append(LayoutZone(
        mi, grid_zone.bottom + margin,
        grid_zone.x - mi - margin,
        page_h - mb - grid_zone.bottom - margin,
    ))
    # Bottom-right corner
    zones.append(LayoutZone(
        grid_zone.right + margin, grid_zone.bottom + margin,
        page_w - mo - grid_zone.right - margin,
        page_h - mb - grid_zone.bottom - margin,
    ))

    # Filter out zones that are too small to be useful
    return [z for z in zones if z.width > 20 and z.height > 20]
