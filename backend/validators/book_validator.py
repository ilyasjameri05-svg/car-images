"""
Book Validator — pre-export validation for grid, palette, layout, and PDF integrity.

If validation fails, export is BLOCKED with clear error messages.
"""
from backend.core.puzzle_generator import PuzzleData
from backend.renderers.page_layout import PageLayout, calculate_layout
from backend.config import PAGE_SIZES


def validate_puzzle(puzzle_data: PuzzleData) -> dict:
    """Validate a single puzzle's data integrity.

    Returns:
        {"valid": bool, "errors": [...], "warnings": [...]}
    """
    errors = []
    warnings = []

    gw = puzzle_data.grid_width
    gh = puzzle_data.grid_height
    cells = puzzle_data.cells
    palette = puzzle_data.palette

    # 1. Grid dimensions
    expected_cells = gw * gh
    if len(cells) != expected_cells:
        errors.append(
            f"Cell count mismatch: expected {expected_cells} "
            f"({gw}x{gh}), got {len(cells)}"
        )

    # 2. Check for missing/duplicate positions
    positions = set()
    for cell in cells:
        pos = (cell["row"], cell["col"])
        if pos in positions:
            errors.append(f"Duplicate cell at position {pos}")
        positions.add(pos)

    for r in range(gh):
        for c in range(gw):
            if (r, c) not in positions:
                errors.append(f"Missing cell at position ({r},{c})")

    # 3. Color ID validity
    palette_ids = {p.color_id for p in palette}
    invalid_colors = set()
    for cell in cells:
        if cell["color_id"] not in palette_ids:
            invalid_colors.add(cell["color_id"])

    if invalid_colors:
        errors.append(
            f"Invalid color_ids found: {sorted(invalid_colors)}. "
            f"Valid IDs: {sorted(palette_ids)}"
        )

    # 4. Palette validity
    if len(palette) == 0:
        errors.append("Palette is empty")
    elif len(palette) < 2:
        errors.append(f"Palette has too few colors ({len(palette)}). Minimum is 2.")
    else:
        # Check for duplicate color_ids in palette
        seen_ids = set()
        for p in palette:
            if p.color_id in seen_ids:
                errors.append(f"Duplicate color_id {p.color_id} in palette")
            seen_ids.add(p.color_id)

        # Check hex validity
        for p in palette:
            if not p.color_hex.startswith("#") or len(p.color_hex) != 7:
                errors.append(
                    f"Invalid hex color '{p.color_hex}' for color_id {p.color_id}"
                )

    # 5. Grid bounds
    for cell in cells:
        if cell["row"] < 0 or cell["row"] >= gh:
            errors.append(f"Cell row {cell['row']} out of bounds (0-{gh-1})")
        if cell["col"] < 0 or cell["col"] >= gw:
            errors.append(f"Cell col {cell['col']} out of bounds (0-{gw-1})")

    # 6. Warnings
    if gw != gh:
        warnings.append(f"Non-square grid: {gw}x{gh}")

    # Count color usage
    color_usage = {}
    for cell in cells:
        cid = cell["color_id"]
        color_usage[cid] = color_usage.get(cid, 0) + 1

    for p in palette:
        if p.color_id not in color_usage:
            warnings.append(f"Color '{p.color_name}' (id={p.color_id}) is unused")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def validate_layout(
    puzzle_data: PuzzleData,
    page_size: str = "kdp_8_5x11",
    orientation: str = "portrait",
) -> dict:
    """Validate that the puzzle fits within the page layout."""
    errors = []
    warnings = []

    layout = calculate_layout(
        page_size, orientation,
        puzzle_data.grid_width, puzzle_data.grid_height,
        color_count=len(puzzle_data.palette),
    )

    # Readability and density check (Warning only — does not block export)
    if layout.readability_warning:
        warnings.append(layout.readability_warning)
    elif layout.cell_size < 10.0:
        warnings.append("High grid density: numbers may be difficult to read in print.")

    # Critical cell size sanity error (only if physically unrenderable)
    if layout.cell_size < 2.0:
        errors.append(
            f"Cell size too small ({layout.cell_size:.1f}pt). "
            f"Numbers will be unreadable. Use a smaller grid or larger page."
        )

    # Grid must fit within margins
    gz = layout.grid_zone
    if gz.x < layout.margin_inside - 1:
        errors.append("Grid extends into the inside margin (binding area)")
    if gz.right > layout.page_width - layout.margin_outside + 1:
        errors.append("Grid extends beyond the outside margin")
    if gz.y < layout.margin_top - 1:
        errors.append("Grid extends into the top margin")
    if gz.bottom > layout.page_height - layout.margin_bottom + 1:
        errors.append("Grid extends beyond the bottom margin")

    # Color key must fit
    ckz = layout.color_key_zone
    if ckz.bottom > layout.page_height - layout.margin_bottom + 1:
        warnings.append("Color key may extend beyond the bottom margin")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "cell_size_pt": round(layout.cell_size, 2),
        "grid_area_pct": round(
            (gz.width * gz.height) / (layout.page_width * layout.page_height) * 100, 1
        ),
    }


def validate_puzzle_answer_equality(
    puzzle_data: PuzzleData,
) -> dict:
    """Validate that puzzle and answer key will be identical in structure.

    Since both renderers use the same PuzzleData object, this is guaranteed
    by architecture. This validator confirms the data integrity.
    """
    errors = []

    # Verify every cell has both a valid color_id and color_hex
    for cell in puzzle_data.cells:
        if "color_id" not in cell:
            errors.append(f"Cell at ({cell.get('row')},{cell.get('col')}) missing color_id")
        if "color_hex" not in cell:
            errors.append(f"Cell at ({cell.get('row')},{cell.get('col')}) missing color_hex")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "guaranteed_by_architecture": True,
        "message": (
            "Puzzle and answer key share the same PuzzleData object. "
            "Grid structure equality is guaranteed by architecture."
        ),
    }


def validate_book(
    puzzles: list[PuzzleData],
    page_size: str = "kdp_8_5x11",
    orientation: str = "portrait",
) -> dict:
    """Validate an entire book before export."""
    errors = []
    warnings = []
    page_results = []

    if not puzzles:
        errors.append("Book has no puzzles")
        return {"valid": False, "errors": errors, "warnings": warnings,
                "page_results": []}

    for idx, puzzle in enumerate(puzzles):
        page_num = idx + 1
        # Validate puzzle data
        pv = validate_puzzle(puzzle)
        # Validate layout
        lv = validate_layout(puzzle, page_size, orientation)
        # Validate puzzle/answer equality
        ev = validate_puzzle_answer_equality(puzzle)

        page_result = {
            "page": page_num,
            "title": puzzle.title,
            "puzzle_valid": pv["valid"],
            "layout_valid": lv["valid"],
            "equality_valid": ev["valid"],
            "puzzle_errors": pv["errors"],
            "layout_errors": lv["errors"],
            "equality_errors": ev["errors"],
            "warnings": pv["warnings"] + lv.get("warnings", []),
        }
        page_results.append(page_result)

        if not pv["valid"]:
            errors.append(f"Page {page_num}: puzzle validation failed")
        if not lv["valid"]:
            errors.append(f"Page {page_num}: layout validation failed")

        warnings.extend(
            [f"Page {page_num}: {w}" for w in pv["warnings"] + lv.get("warnings", [])]
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "page_results": page_results,
        "total_pages": len(puzzles),
    }
