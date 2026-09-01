"""
Image Processor — preprocessing, resize, crop, pad while preserving aspect ratio.

CRITICAL: Never stretch or distort the source image. Always preserve aspect ratio.
"""
import numpy as np
from PIL import Image, ImageFilter, ImageOps


def preprocess_image(
    image: Image.Image,
    target_width: int,
    target_height: int,
) -> Image.Image:
    """Preprocess source image for mosaic conversion.

    - Preserves aspect ratio (never stretches)
    - Centers the main subject
    - Pads with background color when needed
    - Reduces background noise
    """
    # Convert to RGB if needed
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Step 1: Determine the dominant background color for padding
    bg_color = _detect_background_color(image)

    # Step 2: Fit image into target aspect ratio with padding (never stretch)
    fitted = _fit_to_aspect_ratio(image, target_width, target_height, bg_color)

    # Step 3: Resize to target dimensions using high-quality resampling
    resized = fitted.resize((target_width, target_height), Image.LANCZOS)

    # Step 4: Light noise reduction to help quantization
    cleaned = resized.filter(ImageFilter.MedianFilter(size=3))

    return cleaned


def _detect_background_color(image: Image.Image) -> tuple[int, int, int]:
    """Detect the dominant background color by sampling edges."""
    w, h = image.size
    pixels = []

    # Sample pixels from all four edges
    for x in range(w):
        pixels.append(image.getpixel((x, 0)))
        pixels.append(image.getpixel((x, h - 1)))
    for y in range(h):
        pixels.append(image.getpixel((0, y)))
        pixels.append(image.getpixel((w - 1, y)))

    # Return the average color of edge pixels
    arr = np.array(pixels, dtype=np.float64)
    avg = arr.mean(axis=0).astype(int)
    return tuple(avg.tolist())


def _fit_to_aspect_ratio(
    image: Image.Image,
    target_w: int,
    target_h: int,
    bg_color: tuple[int, int, int],
) -> Image.Image:
    """Fit image into target aspect ratio using padding (letterboxing).

    Never crops the subject — only adds padding when aspect ratios differ.
    """
    src_w, src_h = image.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if abs(src_ratio - target_ratio) < 0.01:
        # Aspect ratios are close enough
        return image

    if src_ratio > target_ratio:
        # Source is wider — add top/bottom padding
        new_w = src_w
        new_h = int(src_w / target_ratio)
    else:
        # Source is taller — add left/right padding
        new_h = src_h
        new_w = int(src_h * target_ratio)

    # Create new canvas with background color
    canvas = Image.new("RGB", (new_w, new_h), bg_color)

    # Center the original image on the canvas
    offset_x = (new_w - src_w) // 2
    offset_y = (new_h - src_h) // 2
    canvas.paste(image, (offset_x, offset_y))

    return canvas


def validate_image(image: Image.Image) -> list[str]:
    """Validate that the image is suitable for processing."""
    errors = []

    if image is None:
        errors.append("Image is None")
        return errors

    w, h = image.size
    if w < 50 or h < 50:
        errors.append(f"Image too small ({w}x{h}). Minimum 50x50 pixels.")
    if w > 10000 or h > 10000:
        errors.append(f"Image too large ({w}x{h}). Maximum 10000x10000 pixels.")

    return errors
