"""
Decoration Manager — generates and manages SVG decorations.

Decorations NEVER enter the Color-by-Number grid area. They are placed
in corners, top, bottom, and side areas only.
"""
import os
import math
from pathlib import Path
from backend.config import DECOR_DIR


# ── SVG decoration generators ─────────────────────────────────────────
# Each generator returns an SVG string for a small decoration element.

def _svg_wrap(content: str, size: int = 80) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {size} {size}" width="{size}" height="{size}">'
        f'{content}</svg>'
    )


def _star(cx: float, cy: float, r: float, points: int = 5,
          fill: str = "#FFD700") -> str:
    """Generate a star polygon."""
    coords = []
    for i in range(points * 2):
        angle = math.pi / 2 + (math.pi * i / points)
        radius = r if i % 2 == 0 else r * 0.4
        x = cx + radius * math.cos(angle)
        y = cy - radius * math.sin(angle)
        coords.append(f"{x:.1f},{y:.1f}")
    return f'<polygon points="{" ".join(coords)}" fill="{fill}" />'


def _circle(cx: float, cy: float, r: float, fill: str) -> str:
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" />'


def _paw_print(cx: float, cy: float, scale: float = 1.0) -> str:
    s = scale
    return (
        f'<ellipse cx="{cx}" cy="{cy+8*s}" rx="{10*s}" ry="{12*s}" fill="#795548" />'
        f'<circle cx="{cx-12*s}" cy="{cy-6*s}" r="{5*s}" fill="#795548" />'
        f'<circle cx="{cx-4*s}" cy="{cy-12*s}" r="{5*s}" fill="#795548" />'
        f'<circle cx="{cx+4*s}" cy="{cy-12*s}" r="{5*s}" fill="#795548" />'
        f'<circle cx="{cx+12*s}" cy="{cy-6*s}" r="{5*s}" fill="#795548" />'
    )


def _snowflake(cx: float, cy: float, r: float) -> str:
    lines = ""
    for i in range(6):
        angle = math.radians(i * 60)
        x2 = cx + r * math.cos(angle)
        y2 = cy + r * math.sin(angle)
        lines += (
            f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#90CAF9" stroke-width="2" stroke-linecap="round" />'
        )
        # Branch tips
        bx = cx + r * 0.6 * math.cos(angle)
        by = cy + r * 0.6 * math.sin(angle)
        for offset in [-30, 30]:
            a2 = math.radians(i * 60 + offset)
            tx = bx + r * 0.3 * math.cos(a2)
            ty = by + r * 0.3 * math.sin(a2)
            lines += (
                f'<line x1="{bx:.1f}" y1="{by:.1f}" '
                f'x2="{tx:.1f}" y2="{ty:.1f}" '
                f'stroke="#90CAF9" stroke-width="1.5" stroke-linecap="round" />'
            )
    return lines


def _heart(cx: float, cy: float, s: float, fill: str = "#E91E63") -> str:
    return (
        f'<path d="M{cx},{cy+s*0.3} '
        f'C{cx},{cy-s*0.5} {cx-s},{cy-s*0.5} {cx-s},{cy+s*0.1} '
        f'C{cx-s},{cy+s*0.6} {cx},{cy+s} {cx},{cy+s} '
        f'C{cx},{cy+s} {cx+s},{cy+s*0.6} {cx+s},{cy+s*0.1} '
        f'C{cx+s},{cy-s*0.5} {cx},{cy-s*0.5} {cx},{cy+s*0.3}Z" '
        f'fill="{fill}" />'
    )


def _tree(cx: float, cy: float, s: float) -> str:
    # Simple triangle tree
    return (
        f'<polygon points="{cx},{cy-s*1.2} {cx-s*0.8},{cy+s*0.4} {cx+s*0.8},{cy+s*0.4}" '
        f'fill="#43A047" />'
        f'<rect x="{cx-s*0.15}" y="{cy+s*0.4}" width="{s*0.3}" height="{s*0.4}" '
        f'fill="#795548" />'
    )


def _fish(cx: float, cy: float, s: float) -> str:
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{s*0.8}" ry="{s*0.4}" fill="#1E88E5" />'
        f'<polygon points="{cx+s*0.7},{cy} {cx+s*1.2},{cy-s*0.4} {cx+s*1.2},{cy+s*0.4}" '
        f'fill="#1E88E5" />'
        f'<circle cx="{cx-s*0.3}" cy="{cy-s*0.1}" r="{s*0.08}" fill="white" />'
    )


def _moon(cx: float, cy: float, r: float) -> str:
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FDD835" />'
        f'<circle cx="{cx+r*0.3}" cy="{cy-r*0.2}" r="{r*0.75}" fill="#1A1A2E" />'
    )


def _rocket(cx: float, cy: float, s: float) -> str:
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{s*0.3}" ry="{s}" fill="#E0E0E0" />'
        f'<polygon points="{cx},{cy-s*1.1} {cx-s*0.3},{cy-s*0.6} {cx+s*0.3},{cy-s*0.6}" '
        f'fill="#E53935" />'
        f'<polygon points="{cx-s*0.3},{cy+s*0.6} {cx-s*0.5},{cy+s} {cx},{cy+s*0.6}" '
        f'fill="#FB8C00" />'
        f'<polygon points="{cx+s*0.3},{cy+s*0.6} {cx+s*0.5},{cy+s} {cx},{cy+s*0.6}" '
        f'fill="#FB8C00" />'
        f'<circle cx="{cx}" cy="{cy-s*0.1}" r="{s*0.15}" fill="#1E88E5" />'
    )


# ── Decoration sets per theme ─────────────────────────────────────────

DECORATION_GENERATORS: dict[str, list[tuple[str, callable]]] = {
    "animals": [
        ("paw_print_1", lambda: _svg_wrap(_paw_print(40, 40, 1.0))),
        ("paw_print_2", lambda: _svg_wrap(_paw_print(40, 40, 0.7))),
        ("star", lambda: _svg_wrap(_star(40, 40, 25, fill="#FB8C00"))),
        ("heart", lambda: _svg_wrap(_heart(40, 30, 18, "#E91E63"))),
    ],
    "christmas": [
        ("star", lambda: _svg_wrap(_star(40, 40, 28, fill="#FFD700"))),
        ("tree", lambda: _svg_wrap(_tree(40, 45, 22))),
        ("snowflake", lambda: _svg_wrap(_snowflake(40, 40, 25))),
        ("heart", lambda: _svg_wrap(_heart(40, 30, 18, "#E53935"))),
    ],
    "halloween": [
        ("star", lambda: _svg_wrap(_star(40, 40, 25, fill="#FB8C00"))),
        ("moon", lambda: _svg_wrap(_moon(40, 40, 25))),
        ("bat_star", lambda: _svg_wrap(_star(40, 40, 20, 4, "#424242"))),
    ],
    "space": [
        ("star", lambda: _svg_wrap(_star(40, 40, 25, fill="#FDD835"))),
        ("star_small", lambda: _svg_wrap(_star(40, 40, 15, fill="#BDBDBD"))),
        ("moon", lambda: _svg_wrap(_moon(40, 40, 25))),
        ("rocket", lambda: _svg_wrap(_rocket(40, 40, 20))),
    ],
    "dinosaur": [
        ("star", lambda: _svg_wrap(_star(40, 40, 25, fill="#43A047"))),
        ("paw_print", lambda: _svg_wrap(_paw_print(40, 40, 1.2))),
        ("tree", lambda: _svg_wrap(_tree(40, 45, 22))),
    ],
    "ocean": [
        ("star", lambda: _svg_wrap(_star(40, 40, 25, 5, "#1E88E5"))),
        ("fish", lambda: _svg_wrap(_fish(40, 40, 20))),
        ("wave_dot", lambda: _svg_wrap(_circle(40, 40, 15, "#90CAF9"))),
    ],
    "farm": [
        ("star", lambda: _svg_wrap(_star(40, 40, 25, fill="#FDD835"))),
        ("heart", lambda: _svg_wrap(_heart(40, 30, 18, "#E53935"))),
        ("tree", lambda: _svg_wrap(_tree(40, 45, 22))),
    ],
    "jungle": [
        ("star", lambda: _svg_wrap(_star(40, 40, 25, fill="#43A047"))),
        ("tree", lambda: _svg_wrap(_tree(40, 45, 22))),
        ("paw_print", lambda: _svg_wrap(_paw_print(40, 40, 0.8))),
    ],
    "fantasy": [
        ("star", lambda: _svg_wrap(_star(40, 40, 28, fill="#9C27B0"))),
        ("heart", lambda: _svg_wrap(_heart(40, 30, 18, "#E91E63"))),
        ("moon", lambda: _svg_wrap(_moon(40, 40, 25))),
    ],
    "winter": [
        ("snowflake_1", lambda: _svg_wrap(_snowflake(40, 40, 28))),
        ("snowflake_2", lambda: _svg_wrap(_snowflake(40, 40, 18))),
        ("star", lambda: _svg_wrap(_star(40, 40, 20, fill="#90CAF9"))),
        ("tree", lambda: _svg_wrap(_tree(40, 45, 22))),
    ],
    "summer": [
        ("star", lambda: _svg_wrap(_star(40, 40, 28, fill="#FDD835"))),
        ("heart", lambda: _svg_wrap(_heart(40, 30, 18, "#FB8C00"))),
        ("fish", lambda: _svg_wrap(_fish(40, 40, 20))),
    ],
}


def generate_decorations():
    """Generate all SVG decoration files in the decor/ directory."""
    for theme, generators in DECORATION_GENERATORS.items():
        theme_dir = DECOR_DIR / theme
        theme_dir.mkdir(parents=True, exist_ok=True)
        for name, gen_func in generators:
            filepath = theme_dir / f"{name}.svg"
            if not filepath.exists():
                svg_content = gen_func()
                filepath.write_text(svg_content, encoding="utf-8")


def list_decorations(theme: str) -> list[dict]:
    """List available decorations for a theme."""
    theme_dir = DECOR_DIR / theme
    if not theme_dir.exists():
        return []

    decorations = []
    for svg_file in sorted(theme_dir.glob("*.svg")):
        decorations.append({
            "name": svg_file.stem,
            "theme": theme,
            "path": str(svg_file),
            "filename": svg_file.name,
        })
    return decorations


def get_all_themes() -> list[str]:
    """Return all available decoration themes."""
    return list(DECORATION_GENERATORS.keys())
