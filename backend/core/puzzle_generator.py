"""
Puzzle Generator — the single orchestration point for image → PuzzleData.

CRITICAL: PuzzleData is generated EXACTLY ONCE. Both the puzzle renderer and
answer renderer consume the SAME PuzzleData. This guarantees they are identical.

Pipeline:
    Source Image → preprocess → resolve color count (if auto) → quantize → generate_grid → PuzzleData
"""
from dataclasses import dataclass, field
from typing import Optional, Union
from PIL import Image

from backend.core.image_processor import preprocess_image
from backend.core.color_quantizer import quantize_colors, detect_optimal_color_count
from backend.core.palette_engine import generate_palette, NamedColor
from backend.core.grid_generator import generate_grid


@dataclass
class PuzzleData:
    """Complete puzzle data generated once and used by both renderers.

    This is the SINGLE SOURCE OF TRUTH for a puzzle. Never reprocess
    the source image to create the answer key.
    """
    grid_width: int
    grid_height: int
    cells: list[dict] = field(default_factory=list)
    palette: list[NamedColor] = field(default_factory=list)
    color_count: int = 0  # Resolved integer count
    requested_color_count: Union[int, str] = "auto"
    seed: Optional[int] = None
    title: str = ""
    difficulty: str = "medium"
    source_image_path: str = ""

    def __post_init__(self):
        if not self.color_count and self.palette:
            self.color_count = len(self.palette)

    @property
    def resolved_color_count(self) -> int:
        return len(self.palette) if self.palette else self.color_count

    def get_cell(self, row: int, col: int) -> dict | None:
        for cell in self.cells:
            if cell["row"] == row and cell["col"] == col:
                return cell
        return None

    def to_dict(self) -> dict:
        return {
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "cells": self.cells,
            "palette": [p.to_dict() for p in self.palette],
            "color_count": self.resolved_color_count,
            "resolved_color_count": self.resolved_color_count,
            "requested_color_count": self.requested_color_count,
            "seed": self.seed,
            "title": self.title,
            "difficulty": self.difficulty,
            "source_image_path": self.source_image_path,
        }


def generate_puzzle(
    source_image: Image.Image,
    grid_width: int = 30,
    grid_height: int = 30,
    color_count: Union[int, str] = "auto",
    seed: int | None = None,
    title: str = "",
    difficulty: str = "medium",
    source_image_path: str = "",
) -> PuzzleData:
    """Generate a complete Color-by-Number puzzle from a source image.

    This is the ONLY function that processes the source image. The resulting
    PuzzleData is then used by both the puzzle renderer (numbers) and the
    answer renderer (colors). NEVER call this twice for the same puzzle.

    Args:
        source_image: The source PIL Image.
        grid_width: Number of grid columns (20–60).
        grid_height: Number of grid rows (20–60).
        color_count: Target number of colors (6–20) or 'auto' for intelligent selection.
        seed: Optional seed for deterministic generation.
        title: Puzzle title.
        difficulty: Difficulty level string.
        source_image_path: Path to the original source image file.

    Returns:
        PuzzleData containing the complete grid, palette, and metadata.
    """
    # Step 1: Preprocess — resize, preserve aspect ratio, center subject
    processed = preprocess_image(source_image, grid_width * 10, grid_height * 10)

    # Step 2: Resolve color count if 'auto'
    is_auto = (
        isinstance(color_count, str) and color_count.strip().lower() == "auto"
        or color_count == 0
        or color_count is None
    )

    if is_auto:
        resolved_count = detect_optimal_color_count(
            processed,
            grid_width=grid_width,
            grid_height=grid_height,
            difficulty=difficulty,
            seed=seed,
        )
    else:
        resolved_count = int(color_count)

    # Step 3: Quantize colors — reduce to limited palette via CIELAB K-Means
    quantized, palette_rgb = quantize_colors(processed, resolved_count, seed)

    # Step 4: Generate named palette
    named_palette = generate_palette(palette_rgb)

    # Step 5: Generate grid — map quantized image to cell grid with feature edge weighting
    cells = generate_grid(quantized, grid_width, grid_height, palette_rgb, source_image=processed)

    return PuzzleData(
        grid_width=grid_width,
        grid_height=grid_height,
        cells=cells,
        palette=named_palette,
        color_count=len(named_palette),
        requested_color_count=color_count,
        seed=seed,
        title=title,
        difficulty=difficulty,
        source_image_path=source_image_path,
    )
