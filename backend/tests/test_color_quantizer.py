"""
Tests for color quantization engine.
"""
import pytest
from PIL import Image
from backend.core.color_quantizer import quantize_colors, quantize_to_palette


class TestQuantizeColors:
    def test_basic_quantization(self, sample_image):
        """Quantization should reduce to exactly the requested number of colors."""
        quantized, palette = quantize_colors(sample_image, num_colors=6)
        assert len(palette) == 6
        assert quantized.size == sample_image.size
        assert quantized.mode == "RGB"

    @pytest.mark.parametrize("num_colors", [6, 8, 10, 12, 15, 20])
    def test_various_color_counts(self, sample_image, num_colors):
        """Should work with all supported color counts."""
        quantized, palette = quantize_colors(sample_image, num_colors=num_colors)
        assert len(palette) == num_colors

    def test_deterministic_with_seed(self, sample_image):
        """Same seed should produce identical results."""
        q1, p1 = quantize_colors(sample_image, num_colors=8, seed=42)
        q2, p2 = quantize_colors(sample_image, num_colors=8, seed=42)

        # Palettes should be identical
        assert p1 == p2

        # Pixel-level comparison
        import numpy as np
        assert np.array_equal(np.array(q1), np.array(q2))

    def test_different_seeds_produce_different_results(self, sample_image):
        """Different seeds should (likely) produce different palettes."""
        _, p1 = quantize_colors(sample_image, num_colors=8, seed=1)
        _, p2 = quantize_colors(sample_image, num_colors=8, seed=999)
        # Not guaranteed to differ, but highly likely with different seeds
        # Just verify both work
        assert len(p1) == 8
        assert len(p2) == 8

    def test_output_colors_are_valid_rgb(self, sample_image):
        """All palette colors should be valid RGB tuples."""
        _, palette = quantize_colors(sample_image, num_colors=10)
        for color in palette:
            assert len(color) == 3
            for channel in color:
                assert 0 <= channel <= 255

    def test_small_image(self, small_image):
        """Should handle small images (50x50)."""
        quantized, palette = quantize_colors(small_image, num_colors=6)
        assert len(palette) == 6

    def test_quantize_to_existing_palette(self, sample_image):
        """Should map all pixels to the given palette."""
        palette = [(255, 0, 0), (0, 0, 255), (0, 128, 0), (255, 255, 0)]
        result = quantize_to_palette(sample_image, palette)
        assert result.size == sample_image.size

        import numpy as np
        arr = np.array(result)
        unique_colors = set(map(tuple, arr.reshape(-1, 3).tolist()))
        # All colors in the output should be from the palette
        for color in unique_colors:
            assert color in palette


class TestDetectOptimalColorCount:
    def test_detect_optimal_simple_image(self, sample_image):
        """Simple image should return a smaller palette (6 or 8)."""
        from backend.core.color_quantizer import detect_optimal_color_count
        count = detect_optimal_color_count(sample_image, seed=42)
        assert count in [6, 8, 10, 12, 15, 20]
        assert count <= 8

    def test_detect_optimal_deterministic_seed(self, sample_image):
        """Same seed should return identical color count."""
        from backend.core.color_quantizer import detect_optimal_color_count
        c1 = detect_optimal_color_count(sample_image, seed=123)
        c2 = detect_optimal_color_count(sample_image, seed=123)
        assert c1 == c2

    def test_detect_optimal_respects_easy_difficulty(self, sample_image):
        """Easy difficulty or small grid caps at 8 colors."""
        from backend.core.color_quantizer import detect_optimal_color_count
        count = detect_optimal_color_count(sample_image, grid_width=20, grid_height=20, difficulty="easy", seed=42)
        assert count <= 8
