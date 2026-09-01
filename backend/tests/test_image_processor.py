"""
Tests for image processor.
"""
import pytest
from PIL import Image
from backend.core.image_processor import preprocess_image, validate_image


class TestImageProcessor:
    def test_preserves_aspect_ratio_square(self, sample_image):
        """Square input to square target should not distort."""
        result = preprocess_image(sample_image, 300, 300)
        assert result.size == (300, 300)

    def test_portrait_to_square(self, portrait_image):
        """Portrait image to square target should pad, not stretch."""
        result = preprocess_image(portrait_image, 300, 300)
        assert result.size == (300, 300)
        # Image should not be stretched

    def test_landscape_to_square(self, landscape_image):
        """Landscape image to square target should pad, not stretch."""
        result = preprocess_image(landscape_image, 300, 300)
        assert result.size == (300, 300)

    def test_output_is_rgb(self, sample_image):
        """Output should always be RGB."""
        rgba_img = sample_image.convert("RGBA")
        result = preprocess_image(rgba_img, 200, 200)
        assert result.mode == "RGB"

    def test_validate_good_image(self, sample_image):
        """Valid image should pass validation."""
        errors = validate_image(sample_image)
        assert len(errors) == 0

    def test_validate_too_small(self):
        """Tiny image should fail validation."""
        tiny = Image.new("RGB", (10, 10))
        errors = validate_image(tiny)
        assert len(errors) > 0
        assert "too small" in errors[0].lower()

    def test_validate_none(self):
        """None image should fail validation."""
        errors = validate_image(None)
        assert len(errors) > 0
