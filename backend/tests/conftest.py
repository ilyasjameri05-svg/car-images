"""
Pytest fixtures and shared test utilities.
"""
import os
import sys
import pytest
from pathlib import Path
from PIL import Image
import numpy as np

# Ensure backend is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


@pytest.fixture
def sample_image():
    """Create a simple test image with distinct color regions."""
    img = Image.new("RGB", (200, 200), "#FFFFFF")
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    # Four colored quadrants
    draw.rectangle([0, 0, 100, 100], fill="#E53935")      # Red
    draw.rectangle([100, 0, 200, 100], fill="#1E88E5")     # Blue
    draw.rectangle([0, 100, 100, 200], fill="#43A047")     # Green
    draw.rectangle([100, 100, 200, 200], fill="#FDD835")   # Yellow
    # Center circle
    draw.ellipse([60, 60, 140, 140], fill="#000000")
    return img


@pytest.fixture
def small_image():
    """Create a small 50x50 test image."""
    img = Image.new("RGB", (50, 50), "#FFFFFF")
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 25, 25], fill="#E53935")
    draw.rectangle([25, 0, 50, 25], fill="#1E88E5")
    draw.rectangle([0, 25, 25, 50], fill="#43A047")
    draw.rectangle([25, 25, 50, 50], fill="#FDD835")
    return img


@pytest.fixture
def large_image():
    """Create a larger test image (500x500)."""
    img = Image.new("RGB", (500, 500))
    arr = np.random.RandomState(42).randint(0, 256, (500, 500, 3), dtype=np.uint8)
    return Image.fromarray(arr)


@pytest.fixture
def portrait_image():
    """Create a portrait-oriented image (200x400)."""
    img = Image.new("RGB", (200, 400), "#E3F2FD")
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.ellipse([30, 50, 170, 350], fill="#E53935")
    return img


@pytest.fixture
def landscape_image():
    """Create a landscape-oriented image (400x200)."""
    img = Image.new("RGB", (400, 200), "#E3F2FD")
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 30, 350, 170], fill="#1E88E5")
    return img
