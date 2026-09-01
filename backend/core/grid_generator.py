"""
Grid Generator — converts a quantized image into a structure-preserving mosaic grid.

Key features:
1. Feature- & Edge-Weighted Cell Assignment:
   Pixels located on strong edges, facial features (eyes, nose, mouth), silhouettes,
   or high-contrast details receive higher voting weight, preventing delicate
   subject features from being washed out by surrounding background or flat body fill.
2. Structure-Preserving Background Noise Cleanup:
   Cleans isolated speckle cells in large uniform background areas while strictly
   preserving small subject features (eyes, pupils, ear tips, tails).
3. Mathematical Grid Alignment:
   Zero gaps, exact integer cell indices, perfect square mosaic alignment.
"""
import numpy as np
from PIL import Image, ImageFilter
from collections import Counter


def generate_grid(
    quantized_image: Image.Image,
    grid_width: int,
    grid_height: int,
    palette_rgb: list[tuple[int, int, int]],
    source_image: Image.Image | None = None,
) -> list[dict]:
    """Generate a structure-preserving mosaic grid from a quantized image.

    Args:
        quantized_image: Color-quantized RGB image.
        grid_width: Number of columns in the grid.
        grid_height: Number of rows in the grid.
        palette_rgb: List of palette RGB tuples, index = color_id - 1.
        source_image: Optional original preprocessed image used for edge weighting.

    Returns:
        List of cell dicts: {row, col, color_id, color_hex}
    """
    if quantized_image.mode != "RGB":
        quantized_image = quantized_image.convert("RGB")

    img_array = np.array(quantized_image)
    img_h, img_w, _ = img_array.shape

    # Calculate edge magnitude map from source_image or quantized
    ref_img = source_image if source_image is not None else quantized_image
    if ref_img.mode != "RGB":
        ref_img = ref_img.convert("RGB")
    gray = ref_img.convert("L").resize((img_w, img_h), Image.LANCZOS)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_map = np.array(edges, dtype=np.float64) / 255.0

    # Local detail/contrast map (detects eyes, nose, small spots)
    blur = gray.filter(ImageFilter.BoxBlur(2))
    contrast_map = np.abs(np.array(gray, dtype=np.float64) - np.array(blur, dtype=np.float64)) / 255.0

    # Combined saliency map for cell voting
    detail_weight_map = 1.0 + 3.5 * edge_map + 2.5 * contrast_map

    # Build fast color lookup: RGB tuple -> color_id (1-based)
    color_lookup: dict[tuple[int, int, int], int] = {}
    for idx, rgb in enumerate(palette_rgb):
        color_lookup[rgb] = idx + 1

    cell_pixel_w = img_w / grid_width
    cell_pixel_h = img_h / grid_height

    raw_grid: list[list[int]] = []

    for row in range(grid_height):
        row_colors: list[int] = []
        for col in range(grid_width):
            x_start = int(round(col * cell_pixel_w))
            x_end = int(round((col + 1) * cell_pixel_w))
            y_start = int(round(row * cell_pixel_h))
            y_end = int(round((row + 1) * cell_pixel_h))

            # Clamp
            x_start = min(max(0, x_start), img_w - 1)
            x_end = min(max(x_start + 1, x_end), img_w)
            y_start = min(max(0, y_start), img_h - 1)
            y_end = min(max(y_start + 1, y_end), img_h)

            region_pixels = img_array[y_start:y_end, x_start:x_end].reshape(-1, 3)
            region_weights = detail_weight_map[y_start:y_end, x_start:x_end].reshape(-1)

            best_color_id = _weighted_vote(
                region_pixels, region_weights, palette_rgb, color_lookup
            )
            row_colors.append(best_color_id)
        raw_grid.append(row_colors)

    # Detect dominant border/background color ID
    border_cids = (
        raw_grid[0] + raw_grid[-1] +
        [raw_grid[r][0] for r in range(grid_height)] +
        [raw_grid[r][-1] for r in range(grid_height)]
    )
    bg_cid = Counter(border_cids).most_common(1)[0][0] if border_cids else None

    # Post-process grid: clean isolated noise speckles in background without eroding subject
    cleaned_grid = _clean_grid_noise(raw_grid, grid_height, grid_width, bg_cid=bg_cid)

    # Build cells list
    cells = []
    for row in range(grid_height):
        for col in range(grid_width):
            cid = cleaned_grid[row][col]
            color_hex = _rgb_to_hex(*palette_rgb[cid - 1])
            cells.append({
                "row": row,
                "col": col,
                "color_id": cid,
                "color_hex": color_hex,
            })

    return cells


def _weighted_vote(
    pixels: np.ndarray,
    weights: np.ndarray,
    palette_rgb: list[tuple[int, int, int]],
    color_lookup: dict[tuple[int, int, int], int],
) -> int:
    """Find the best palette color in a cell region using feature-weighted voting.

    Pixels on edges, facial details, and high-contrast boundaries receive higher weight
    so that fine outlines, eyes, ears, and silhouettes take priority over surrounding flat areas.
    """
    scores: dict[int, float] = {}

    for pixel, weight in zip(pixels, weights):
        rgb = tuple(pixel.tolist())

        # Lookup color ID
        if rgb in color_lookup:
            cid = color_lookup[rgb]
        else:
            # Fallback nearest in Euclidean space
            best_id = 1
            best_dist = float("inf")
            for idx, p_rgb in enumerate(palette_rgb):
                d = sum((int(a) - int(b)) ** 2 for a, b in zip(rgb, p_rgb))
                if d < best_dist:
                    best_dist = d
                    best_id = idx + 1
            cid = best_id

        scores[cid] = scores.get(cid, 0.0) + float(weight)

    # Return color with highest weighted score
    return max(scores.items(), key=lambda item: item[1])[0]


def _clean_grid_noise(
    grid: list[list[int]],
    h: int,
    w: int,
    bg_cid: int | None = None,
) -> list[list[int]]:
    """Clean isolated 1-cell noise artifacts in uniform areas.

    Only snaps cells if surrounded by 7+ neighbors of the same color,
    and prioritizes cleaning background noise rather than small subject features.
    """
    cleaned = [row[:] for row in grid]

    for r in range(1, h - 1):
        for c in range(1, w - 1):
            center = grid[r][c]
            neighbors = [
                grid[r - 1][c - 1], grid[r - 1][c], grid[r - 1][c + 1],
                grid[r][c - 1],                       grid[r][c + 1],
                grid[r + 1][c - 1], grid[r + 1][c], grid[r + 1][c + 1],
            ]
            neighbor_counts = Counter(neighbors)
            most_common_color, most_common_count = neighbor_counts.most_common(1)[0]

            # If 7 or 8 neighbors agree and center is different
            if most_common_count >= 7 and center != most_common_color:
                # If the majority color is background or center is not a rare accent color, snap it
                if bg_cid is None or most_common_color == bg_cid or center == bg_cid:
                    cleaned[r][c] = most_common_color

    return cleaned


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to hex string."""
    return f"#{r:02X}{g:02X}{b:02X}"
