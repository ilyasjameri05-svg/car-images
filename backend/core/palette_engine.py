"""
Palette Engine — generates named color palettes from quantized colors.

CRITICAL RULE: One number = exactly one color. Never reassign.
Uses CIELAB perceptual matching to assign clear, distinct, child-friendly color names.
"""
import math
from dataclasses import dataclass
import numpy as np


@dataclass
class NamedColor:
    color_id: int
    color_name: str
    color_hex: str

    def to_dict(self) -> dict:
        return {
            "color_id": self.color_id,
            "color_name": self.color_name,
            "color_hex": self.color_hex,
        }


# ── Named color reference database ────────────────────────────────────
# 70+ carefully chosen colors with distinct human-readable names
NAMED_COLORS: list[tuple[str, str]] = [
    # Whites & Grays
    ("White", "#FFFFFF"),
    ("Off-White", "#F8F9FA"),
    ("Light Gray", "#D6D6D6"),
    ("Silver", "#B0BEC5"),
    ("Medium Gray", "#9E9E9E"),
    ("Dark Gray", "#616161"),
    ("Charcoal", "#37474F"),
    ("Black", "#000000"),
    # Reds
    ("Red", "#E53935"),
    ("Bright Red", "#FF1744"),
    ("Dark Red", "#B71C1C"),
    ("Crimson", "#DC143C"),
    ("Light Red", "#EF9A9A"),
    ("Ruby", "#C2185B"),
    # Pinks
    ("Pink", "#E91E63"),
    ("Light Pink", "#F8BBD0"),
    ("Hot Pink", "#FF4081"),
    ("Rose", "#FF007F"),
    ("Bubblegum", "#F48FB1"),
    # Oranges
    ("Orange", "#FB8C00"),
    ("Bright Orange", "#FF6D00"),
    ("Dark Orange", "#E65100"),
    ("Light Orange", "#FFB74D"),
    ("Peach", "#FFAB91"),
    ("Tangerine", "#FFA000"),
    # Yellows
    ("Yellow", "#FDD835"),
    ("Bright Yellow", "#FFEA00"),
    ("Gold", "#FFD700"),
    ("Light Yellow", "#FFF9C4"),
    ("Amber", "#FFC107"),
    ("Lemon", "#FFF176"),
    # Greens
    ("Green", "#43A047"),
    ("Dark Green", "#1B5E20"),
    ("Light Green", "#A5D6A7"),
    ("Lime Green", "#7CB342"),
    ("Emerald Green", "#2E7D32"),
    ("Mint Green", "#80CBC4"),
    ("Forest Green", "#2E7D32"),
    ("Olive Green", "#689F38"),
    ("Pastel Green", "#C8E6C9"),
    # Blues
    ("Blue", "#1E88E5"),
    ("Bright Blue", "#0091EA"),
    ("Dark Blue", "#0D47A1"),
    ("Light Blue", "#90CAF9"),
    ("Sky Blue", "#87CEEB"),
    ("Navy Blue", "#1A237E"),
    ("Royal Blue", "#304FFE"),
    ("Cyan", "#00BCD4"),
    ("Teal", "#00897B"),
    ("Turquoise", "#00ACC1"),
    ("Aquamarine", "#4DD0E1"),
    ("Ice Blue", "#E1F5FE"),
    # Purples
    ("Purple", "#8E24AA"),
    ("Dark Purple", "#4A148C"),
    ("Light Purple", "#CE93D8"),
    ("Lavender", "#B39DDB"),
    ("Violet", "#7B1FA2"),
    ("Indigo", "#3949AB"),
    ("Magenta", "#D81B60"),
    ("Plum", "#6A1B9A"),
    # Browns
    ("Brown", "#795548"),
    ("Dark Brown", "#3E2723"),
    ("Light Brown", "#A1887F"),
    ("Tan", "#D2B48C"),
    ("Chocolate Brown", "#5D4037"),
    ("Caramel", "#8D6E63"),
    ("Beige", "#F5F5DC"),
    ("Sand", "#E0C39E"),
    ("Coffee", "#4E342E"),
    # Warm / Coral tones
    ("Coral", "#FF7043"),
    ("Salmon", "#FA8072"),
    ("Terracotta", "#D84315"),
    ("Maroon", "#880E4F"),
    ("Burgundy", "#800020"),
    ("Khaki", "#C3B091"),
    ("Cream", "#FFFDD0"),
]


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex string to RGB tuple."""
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB tuple to hex string."""
    return f"#{r:02X}{g:02X}{b:02X}"


def _color_distance(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    """Euclidean distance between two RGB colors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def _rgb_to_lab_single(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    """Convert a single RGB tuple to CIELAB."""
    r, g, b = [x / 255.0 for x in rgb]
    r = ((r + 0.055) / 1.055) ** 2.4 if r > 0.04045 else r / 12.92
    g = ((g + 0.055) / 1.055) ** 2.4 if g > 0.04045 else g / 12.92
    b = ((b + 0.055) / 1.055) ** 2.4 if b > 0.04045 else b / 12.92

    x = (r * 0.4124564 + g * 0.3575761 + b * 0.1804375) / 0.95047
    y = (r * 0.2126729 + g * 0.7151522 + b * 0.0721750) / 1.00000
    z = (r * 0.0193339 + g * 0.1191920 + b * 0.9503041) / 1.08883

    delta = 6.0 / 29.0
    fx = x ** (1.0 / 3.0) if x > delta ** 3 else (x / (3.0 * delta ** 2)) + (4.0 / 29.0)
    fy = y ** (1.0 / 3.0) if y > delta ** 3 else (y / (3.0 * delta ** 2)) + (4.0 / 29.0)
    fz = z ** (1.0 / 3.0) if z > delta ** 3 else (z / (3.0 * delta ** 2)) + (4.0 / 29.0)

    L = 116.0 * fy - 16.0
    A = 500.0 * (fx - fy)
    B = 200.0 * (fy - fz)
    return (L, A, B)


# Precompute LAB for reference colors
NAMED_COLORS_LAB = [
    (name, _hex_to_rgb(hex_c), _rgb_to_lab_single(_hex_to_rgb(hex_c)))
    for name, hex_c in NAMED_COLORS
]


def generate_palette(
    colors_rgb: list[tuple[int, int, int]],
) -> list[NamedColor]:
    """Generate a named palette from a list of RGB colors.

    Uses CIELAB perceptual distance to match each color to the best
    human-readable reference name. Ensures no duplicate names.

    Args:
        colors_rgb: List of RGB tuples from color quantization.

    Returns:
        List of NamedColor, each with a unique color_id starting from 1.
    """
    used_names: set[str] = set()
    palette: list[NamedColor] = []

    for idx, rgb in enumerate(colors_rgb):
        color_id = idx + 1
        color_hex = _rgb_to_hex(*rgb)
        rgb_lab = _rgb_to_lab_single(rgb)

        # Find nearest named color in CIELAB space
        best_name = "Color"
        best_dist = float("inf")
        for name, ref_rgb, ref_lab in NAMED_COLORS_LAB:
            d = math.sqrt(
                (rgb_lab[0] - ref_lab[0]) ** 2 +
                (rgb_lab[1] - ref_lab[1]) ** 2 +
                (rgb_lab[2] - ref_lab[2]) ** 2
            )
            if d < best_dist:
                best_dist = d
                best_name = name

        # Ensure unique name
        final_name = best_name
        counter = 2
        while final_name in used_names:
            final_name = f"{best_name} {counter}"
            counter += 1
        used_names.add(final_name)

        palette.append(NamedColor(
            color_id=color_id,
            color_name=final_name,
            color_hex=color_hex,
        ))

    return palette


def get_preset_palette(name: str) -> list[NamedColor] | None:
    """Return a preset palette by name, or None if not found."""
    presets = {
        "basic": [
            NamedColor(1, "White", "#FFFFFF"),
            NamedColor(2, "Black", "#000000"),
            NamedColor(3, "Red", "#E53935"),
            NamedColor(4, "Blue", "#1E88E5"),
            NamedColor(5, "Green", "#43A047"),
            NamedColor(6, "Yellow", "#FDD835"),
            NamedColor(7, "Orange", "#FB8C00"),
            NamedColor(8, "Purple", "#9C27B0"),
            NamedColor(9, "Pink", "#E91E63"),
            NamedColor(10, "Brown", "#795548"),
        ],
        "pastel": [
            NamedColor(1, "White", "#FFFFFF"),
            NamedColor(2, "Light Pink", "#F8BBD0"),
            NamedColor(3, "Light Blue", "#90CAF9"),
            NamedColor(4, "Light Green", "#A5D6A7"),
            NamedColor(5, "Light Yellow", "#FFF9C4"),
            NamedColor(6, "Light Purple", "#CE93D8"),
            NamedColor(7, "Peach", "#FFAB91"),
            NamedColor(8, "Light Gray", "#BDBDBD"),
            NamedColor(9, "Mint", "#98FF98"),
            NamedColor(10, "Lavender", "#E6E6FA"),
        ],
        "warm": [
            NamedColor(1, "White", "#FFFFFF"),
            NamedColor(2, "Red", "#E53935"),
            NamedColor(3, "Orange", "#FB8C00"),
            NamedColor(4, "Yellow", "#FDD835"),
            NamedColor(5, "Brown", "#795548"),
            NamedColor(6, "Coral", "#FF7F50"),
            NamedColor(7, "Gold", "#FFD700"),
            NamedColor(8, "Tan", "#D2B48C"),
            NamedColor(9, "Pink", "#E91E63"),
            NamedColor(10, "Dark Brown", "#3E2723"),
        ],
        "cool": [
            NamedColor(1, "White", "#FFFFFF"),
            NamedColor(2, "Blue", "#1E88E5"),
            NamedColor(3, "Green", "#43A047"),
            NamedColor(4, "Purple", "#9C27B0"),
            NamedColor(5, "Teal", "#008080"),
            NamedColor(6, "Cyan", "#00BCD4"),
            NamedColor(7, "Dark Blue", "#0D47A1"),
            NamedColor(8, "Indigo", "#3F51B5"),
            NamedColor(9, "Light Blue", "#90CAF9"),
            NamedColor(10, "Emerald", "#2E7D32"),
        ],
    }
    return presets.get(name)
