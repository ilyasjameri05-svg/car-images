"""
Placeholder Image Provider — generates colorful geometric/abstract illustrations locally.

This is ONLY a fallback/testing provider. It is NOT the final AI image generation
solution. It generates recognizable shapes with flat colors suitable for testing
the mosaic pipeline without requiring an API key.
"""
import math
import random
from PIL import Image, ImageDraw
from backend.providers.base import ImageGenerationProvider


class PlaceholderProvider(ImageGenerationProvider):
    """Local fallback provider that generates colorful geometric art.

    Always available, no API key required. Good for testing and development.
    NOT intended as a production image generator.
    """

    @property
    def name(self) -> str:
        return "Placeholder (Local)"

    @property
    def is_available(self) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        seed: int | None = None,
    ) -> Image.Image:
        """Generate a colorful geometric illustration from a prompt."""
        rng = random.Random(seed if seed is not None else hash(prompt))

        img = Image.new("RGB", (width, height), "#FFFFFF")
        draw = ImageDraw.Draw(img)

        # Choose a background color
        bg_colors = ["#E8F5E9", "#E3F2FD", "#FFF3E0", "#FCE4EC",
                      "#F3E5F5", "#E0F7FA", "#FFF8E1", "#E8EAF6"]
        bg = rng.choice(bg_colors)
        draw.rectangle([0, 0, width, height], fill=bg)

        # Parse prompt for shape hints
        prompt_lower = prompt.lower()

        # Determine shape type based on prompt keywords
        if any(w in prompt_lower for w in ["cat", "dog", "fox", "bear", "rabbit"]):
            _draw_animal_shape(draw, width, height, rng, prompt_lower)
        elif any(w in prompt_lower for w in ["fish", "whale", "dolphin", "shark"]):
            _draw_fish_shape(draw, width, height, rng)
        elif any(w in prompt_lower for w in ["bird", "owl", "penguin", "parrot"]):
            _draw_bird_shape(draw, width, height, rng)
        elif any(w in prompt_lower for w in ["tree", "flower", "plant", "forest"]):
            _draw_plant_shape(draw, width, height, rng)
        elif any(w in prompt_lower for w in ["star", "rocket", "planet", "moon"]):
            _draw_space_shape(draw, width, height, rng)
        elif any(w in prompt_lower for w in ["house", "castle", "barn", "building"]):
            _draw_building_shape(draw, width, height, rng)
        else:
            _draw_abstract_shape(draw, width, height, rng)

        return img


def _bright_color(rng: random.Random) -> str:
    """Generate a bright, saturated color."""
    colors = [
        "#E53935", "#D81B60", "#8E24AA", "#5E35B1",
        "#3949AB", "#1E88E5", "#039BE5", "#00ACC1",
        "#00897B", "#43A047", "#7CB342", "#C0CA33",
        "#FDD835", "#FFB300", "#FB8C00", "#F4511E",
        "#6D4C41", "#546E7A", "#EC407A", "#AB47BC",
    ]
    return rng.choice(colors)


def _draw_animal_shape(draw: ImageDraw.Draw, w: int, h: int,
                        rng: random.Random, prompt: str):
    """Draw a simplified animal shape."""
    cx, cy = w // 2, h // 2
    body_color = _bright_color(rng)
    accent = _bright_color(rng)

    # Body (large oval)
    body_w, body_h = w * 0.35, h * 0.3
    draw.ellipse([cx - body_w, cy - body_h * 0.5,
                  cx + body_w, cy + body_h * 1.2], fill=body_color)

    # Head (circle on top)
    head_r = w * 0.2
    head_cy = cy - body_h * 0.6
    draw.ellipse([cx - head_r, head_cy - head_r,
                  cx + head_r, head_cy + head_r], fill=body_color)

    # Ears
    ear_size = head_r * 0.5
    draw.ellipse([cx - head_r * 0.8 - ear_size * 0.5, head_cy - head_r - ear_size,
                  cx - head_r * 0.8 + ear_size * 0.5, head_cy - head_r + ear_size * 0.3],
                 fill=accent)
    draw.ellipse([cx + head_r * 0.8 - ear_size * 0.5, head_cy - head_r - ear_size,
                  cx + head_r * 0.8 + ear_size * 0.5, head_cy - head_r + ear_size * 0.3],
                 fill=accent)

    # Eyes
    eye_r = head_r * 0.12
    draw.ellipse([cx - head_r * 0.35 - eye_r, head_cy - eye_r * 1.5,
                  cx - head_r * 0.35 + eye_r, head_cy + eye_r * 1.5], fill="#000000")
    draw.ellipse([cx + head_r * 0.35 - eye_r, head_cy - eye_r * 1.5,
                  cx + head_r * 0.35 + eye_r, head_cy + eye_r * 1.5], fill="#000000")

    # Nose
    nose_r = head_r * 0.1
    draw.ellipse([cx - nose_r, head_cy + head_r * 0.2 - nose_r,
                  cx + nose_r, head_cy + head_r * 0.2 + nose_r], fill=accent)

    # Legs
    leg_w = body_w * 0.25
    leg_h = h * 0.15
    for lx in [cx - body_w * 0.5, cx - body_w * 0.15,
               cx + body_w * 0.15, cx + body_w * 0.5]:
        draw.rectangle([lx - leg_w * 0.5, cy + body_h * 0.8,
                        lx + leg_w * 0.5, cy + body_h * 0.8 + leg_h],
                       fill=body_color)

    # Ground
    draw.rectangle([0, cy + body_h * 0.8 + leg_h,
                    w, h], fill="#A5D6A7")


def _draw_fish_shape(draw: ImageDraw.Draw, w: int, h: int, rng: random.Random):
    cx, cy = w // 2, h // 2
    color = _bright_color(rng)
    # Water background
    draw.rectangle([0, h * 0.2, w, h], fill="#90CAF9")
    # Body
    draw.ellipse([cx - w * 0.3, cy - h * 0.15,
                  cx + w * 0.2, cy + h * 0.15], fill=color)
    # Tail
    draw.polygon([(cx + w * 0.15, cy),
                  (cx + w * 0.35, cy - h * 0.15),
                  (cx + w * 0.35, cy + h * 0.15)], fill=color)
    # Eye
    draw.ellipse([cx - w * 0.15, cy - h * 0.04,
                  cx - w * 0.1, cy + h * 0.04], fill="#FFFFFF")
    draw.ellipse([cx - w * 0.14, cy - h * 0.02,
                  cx - w * 0.11, cy + h * 0.02], fill="#000000")
    # Fin
    accent = _bright_color(rng)
    draw.polygon([(cx - w * 0.05, cy - h * 0.12),
                  (cx + w * 0.05, cy - h * 0.25),
                  (cx + w * 0.1, cy - h * 0.12)], fill=accent)


def _draw_bird_shape(draw: ImageDraw.Draw, w: int, h: int, rng: random.Random):
    cx, cy = w // 2, h // 2
    color = _bright_color(rng)
    wing_color = _bright_color(rng)
    # Sky
    draw.rectangle([0, 0, w, h * 0.7], fill="#E3F2FD")
    draw.rectangle([0, h * 0.7, w, h], fill="#A5D6A7")
    # Body
    draw.ellipse([cx - w * 0.15, cy - h * 0.12,
                  cx + w * 0.15, cy + h * 0.15], fill=color)
    # Head
    head_r = w * 0.1
    draw.ellipse([cx - head_r, cy - h * 0.22,
                  cx + head_r, cy - h * 0.05], fill=color)
    # Wing
    draw.ellipse([cx - w * 0.2, cy - h * 0.05,
                  cx + w * 0.05, cy + h * 0.1], fill=wing_color)
    # Eye
    draw.ellipse([cx - w * 0.03, cy - h * 0.17,
                  cx + w * 0.02, cy - h * 0.13], fill="#000000")
    # Beak
    draw.polygon([(cx + head_r * 0.7, cy - h * 0.13),
                  (cx + head_r * 1.5, cy - h * 0.11),
                  (cx + head_r * 0.7, cy - h * 0.09)], fill="#FB8C00")
    # Legs
    draw.line([(cx - w * 0.03, cy + h * 0.15),
               (cx - w * 0.05, cy + h * 0.25)], fill="#FB8C00", width=3)
    draw.line([(cx + w * 0.03, cy + h * 0.15),
               (cx + w * 0.05, cy + h * 0.25)], fill="#FB8C00", width=3)


def _draw_plant_shape(draw: ImageDraw.Draw, w: int, h: int, rng: random.Random):
    cx, cy = w // 2, h // 2
    # Sky and ground
    draw.rectangle([0, 0, w, h * 0.6], fill="#E3F2FD")
    draw.rectangle([0, h * 0.6, w, h], fill="#A5D6A7")
    # Trunk
    draw.rectangle([cx - w * 0.04, cy - h * 0.05,
                    cx + w * 0.04, h * 0.65], fill="#795548")
    # Canopy layers
    colors = ["#2E7D32", "#43A047", "#66BB6A", "#81C784"]
    for i, c in enumerate(colors):
        layer_w = w * (0.35 - i * 0.06)
        layer_y = cy - h * (0.1 + i * 0.1)
        draw.polygon([(cx, layer_y - h * 0.12),
                      (cx - layer_w, layer_y + h * 0.08),
                      (cx + layer_w, layer_y + h * 0.08)], fill=c)
    # Flowers
    for _ in range(5):
        fx = rng.randint(int(w * 0.1), int(w * 0.9))
        fy = rng.randint(int(h * 0.65), int(h * 0.85))
        fc = _bright_color(rng)
        r = w * 0.02
        draw.ellipse([fx - r, fy - r, fx + r, fy + r], fill=fc)


def _draw_space_shape(draw: ImageDraw.Draw, w: int, h: int, rng: random.Random):
    # Dark space background
    draw.rectangle([0, 0, w, h], fill="#1A1A2E")
    # Stars
    for _ in range(40):
        sx = rng.randint(0, w)
        sy = rng.randint(0, h)
        sr = rng.randint(1, 3)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill="#FFFFFF")
    cx, cy = w // 2, h // 2
    # Planet
    planet_r = w * 0.2
    draw.ellipse([cx - planet_r, cy - planet_r,
                  cx + planet_r, cy + planet_r], fill="#1E88E5")
    # Ring
    draw.arc([cx - planet_r * 1.5, cy - planet_r * 0.3,
              cx + planet_r * 1.5, cy + planet_r * 0.3],
             0, 360, fill="#FDD835", width=4)
    # Small moon
    draw.ellipse([cx + planet_r * 1.2, cy - planet_r * 0.8,
                  cx + planet_r * 1.5, cy - planet_r * 0.5], fill="#BDBDBD")


def _draw_building_shape(draw: ImageDraw.Draw, w: int, h: int, rng: random.Random):
    # Sky
    draw.rectangle([0, 0, w, h * 0.5], fill="#E3F2FD")
    draw.rectangle([0, h * 0.5, w, h], fill="#A5D6A7")
    cx, cy = w // 2, h // 2
    wall_color = _bright_color(rng)
    roof_color = _bright_color(rng)
    # Walls
    bw, bh = w * 0.4, h * 0.3
    draw.rectangle([cx - bw, cy - bh * 0.3,
                    cx + bw, cy + bh], fill=wall_color)
    # Roof
    draw.polygon([(cx, cy - bh * 0.7),
                  (cx - bw * 1.2, cy - bh * 0.3),
                  (cx + bw * 1.2, cy - bh * 0.3)], fill=roof_color)
    # Door
    draw.rectangle([cx - bw * 0.15, cy + bh * 0.3,
                    cx + bw * 0.15, cy + bh], fill="#795548")
    # Windows
    win_color = "#FDD835"
    for wx in [-0.5, 0.5]:
        for wy in [-0.1, 0.3]:
            draw.rectangle([cx + bw * wx - bw * 0.12, cy + bh * wy - bh * 0.08,
                            cx + bw * wx + bw * 0.12, cy + bh * wy + bh * 0.08],
                           fill=win_color)


def _draw_abstract_shape(draw: ImageDraw.Draw, w: int, h: int, rng: random.Random):
    """Fallback: draw a colorful abstract composition."""
    cx, cy = w // 2, h // 2
    # Background gradient-like effect
    for i in range(5):
        color = _bright_color(rng)
        r = w * (0.4 - i * 0.05)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    # Some geometric accents
    for _ in range(8):
        shape = rng.choice(["rect", "circle", "triangle"])
        color = _bright_color(rng)
        x = rng.randint(int(w * 0.1), int(w * 0.9))
        y = rng.randint(int(h * 0.1), int(h * 0.9))
        size = rng.randint(int(w * 0.05), int(w * 0.15))
        if shape == "rect":
            draw.rectangle([x, y, x + size, y + size], fill=color)
        elif shape == "circle":
            draw.ellipse([x, y, x + size, y + size], fill=color)
        else:
            draw.polygon([(x + size // 2, y),
                          (x, y + size),
                          (x + size, y + size)], fill=color)
