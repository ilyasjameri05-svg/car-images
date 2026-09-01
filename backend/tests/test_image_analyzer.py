"""
Tests for image analyzer.
"""
import pytest
from PIL import Image, ImageDraw
from backend.core.image_analyzer import analyze_image


class TestImageAnalyzer:
    def test_analyze_good_image(self, sample_image):
        """Image with distinct colors should score well."""
        result = analyze_image(sample_image)
        assert "image_quality" in result
        assert "color_separation" in result
        assert "contrast" in result
        assert "mosaic_suitability" in result
        assert "subject_clarity" in result
        assert "recommendation" in result
        assert "is_suitable" in result
        assert 0 <= result["image_quality"] <= 100
        assert 0 <= result["mosaic_suitability"] <= 100

    def test_analyze_uniform_image(self):
        """Completely uniform image should score poorly."""
        img = Image.new("RGB", (200, 200), "#808080")
        result = analyze_image(img)
        assert result["contrast"] < 20  # Very low contrast

    def test_analyze_high_contrast(self):
        """Black and white image should have good contrast."""
        img = Image.new("RGB", (200, 200))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 100, 200], fill="#000000")
        draw.rectangle([100, 0, 200, 200], fill="#FFFFFF")
        result = analyze_image(img)
        assert result["contrast"] > 50

    def test_recommendation_types(self, sample_image):
        """Recommendation should be one of the expected strings."""
        result = analyze_image(sample_image)
        valid = ["GOOD FOR COLOR-BY-NUMBER", "IMAGE NEEDS IMPROVEMENT", "IMAGE NOT SUITABLE"]
        assert result["recommendation"] in valid

    def test_issues_are_list(self, sample_image):
        result = analyze_image(sample_image)
        assert isinstance(result["issues"], list)
