"""
Tests for palette engine.
"""
import pytest
from backend.core.palette_engine import (
    generate_palette, NamedColor, get_preset_palette,
    _hex_to_rgb, _rgb_to_hex, _color_distance,
)


class TestPaletteEngine:
    def test_generate_palette_basic(self):
        """Should generate named colors for a list of RGB values."""
        colors = [(255, 0, 0), (0, 0, 255), (0, 128, 0)]
        palette = generate_palette(colors)
        assert len(palette) == 3
        assert all(isinstance(p, NamedColor) for p in palette)

    def test_color_ids_start_at_one(self):
        """Color IDs should be 1-based."""
        colors = [(255, 0, 0), (0, 0, 255)]
        palette = generate_palette(colors)
        assert palette[0].color_id == 1
        assert palette[1].color_id == 2

    def test_unique_names(self):
        """All color names should be unique."""
        # Use similar colors that might map to the same named color
        colors = [(200, 50, 50), (210, 40, 40), (220, 60, 60)]
        palette = generate_palette(colors)
        names = [p.color_name for p in palette]
        assert len(names) == len(set(names)), f"Duplicate names: {names}"

    def test_hex_format(self):
        """All hex values should be properly formatted."""
        colors = [(128, 64, 200)]
        palette = generate_palette(colors)
        assert palette[0].color_hex.startswith("#")
        assert len(palette[0].color_hex) == 7

    def test_to_dict(self):
        """to_dict should include all required fields."""
        nc = NamedColor(1, "Red", "#FF0000")
        d = nc.to_dict()
        assert d["color_id"] == 1
        assert d["color_name"] == "Red"
        assert d["color_hex"] == "#FF0000"

    def test_preset_palettes(self):
        """Preset palettes should be loadable."""
        for name in ["basic", "pastel", "warm", "cool"]:
            palette = get_preset_palette(name)
            assert palette is not None
            assert len(palette) == 10

    def test_preset_palette_not_found(self):
        """Unknown presets should return None."""
        assert get_preset_palette("nonexistent") is None

    def test_hex_rgb_conversion(self):
        assert _hex_to_rgb("#FF0000") == (255, 0, 0)
        assert _hex_to_rgb("#00FF00") == (0, 255, 0)
        assert _rgb_to_hex(255, 0, 0) == "#FF0000"
        assert _rgb_to_hex(0, 128, 255) == "#0080FF"

    def test_color_distance(self):
        """Distance between identical colors should be 0."""
        assert _color_distance((0, 0, 0), (0, 0, 0)) == 0
        assert _color_distance((255, 255, 255), (255, 255, 255)) == 0
        # Distance between black and white
        assert _color_distance((0, 0, 0), (255, 255, 255)) > 400

    def test_one_number_one_color_rule(self):
        """One color_id must always map to exactly one color."""
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        palette = generate_palette(colors)

        id_to_color = {}
        for p in palette:
            if p.color_id in id_to_color:
                assert id_to_color[p.color_id] == p.color_hex, (
                    f"Color ID {p.color_id} maps to multiple colors!"
                )
            id_to_color[p.color_id] = p.color_hex
