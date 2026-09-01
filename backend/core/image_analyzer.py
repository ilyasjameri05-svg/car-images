"""
Image Analyzer — evaluates image quality for mosaic suitability.

Provides quantitative scores and human-readable recommendations.
"""
import numpy as np
from PIL import Image, ImageFilter


def analyze_image(image: Image.Image) -> dict:
    """Analyze an image for Color-by-Number mosaic suitability.

    Returns a dict with quality scores (0–100) and recommendations.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")

    img_array = np.array(image, dtype=np.float64)
    h, w, _ = img_array.shape

    # 1. Subject clarity — edge density in center vs edges
    subject_clarity = _score_subject_clarity(image)

    # 2. Color separation — how distinct are the dominant colors
    color_separation = _score_color_separation(img_array)

    # 3. Contrast — standard deviation of luminance
    contrast = _score_contrast(img_array)

    # 4. Background complexity — how uniform the background edges are
    bg_complexity = _score_background_simplicity(img_array)

    # 5. Detail density — how fine-grained the textures are
    detail_density = _score_detail_density(image)

    # Composite mosaic suitability score
    mosaic_suitability = (
        subject_clarity * 0.25 +
        color_separation * 0.25 +
        contrast * 0.20 +
        bg_complexity * 0.15 +
        (100 - detail_density) * 0.15  # Less detail = better for mosaic
    )

    # Overall image quality (for general quality, not mosaic-specific)
    image_quality = (
        subject_clarity * 0.3 +
        color_separation * 0.3 +
        contrast * 0.4
    )

    # Generate issues and recommendation
    issues = []
    if subject_clarity < 40:
        issues.append("Subject is not clearly defined — try a more centered composition")
    if color_separation < 40:
        issues.append("Colors are too similar — image needs more distinct color regions")
    if contrast < 30:
        issues.append("Low contrast — image may produce a flat-looking mosaic")
    if bg_complexity < 35:
        issues.append("Background is too complex — simpler backgrounds work better")
    if detail_density > 75:
        issues.append("Too many fine details — these will be lost in the mosaic grid")

    is_suitable = mosaic_suitability >= 50 and len(issues) <= 1

    if is_suitable:
        recommendation = "GOOD FOR COLOR-BY-NUMBER"
    elif mosaic_suitability >= 35:
        recommendation = "IMAGE NEEDS IMPROVEMENT"
    else:
        recommendation = "IMAGE NOT SUITABLE"

    from backend.core.color_quantizer import detect_optimal_color_count
    recommended_colors = detect_optimal_color_count(image)

    return {
        "image_quality": round(min(100, max(0, image_quality)), 1),
        "color_separation": round(min(100, max(0, color_separation)), 1),
        "contrast": round(min(100, max(0, contrast)), 1),
        "mosaic_suitability": round(min(100, max(0, mosaic_suitability)), 1),
        "subject_clarity": round(min(100, max(0, subject_clarity)), 1),
        "recommended_color_count": recommended_colors,
        "recommendation": recommendation,
        "is_suitable": is_suitable,
        "issues": issues,
    }


def _score_subject_clarity(image: Image.Image) -> float:
    """Score how clearly defined the subject is (center vs edges)."""
    gray = image.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_array = np.array(edges, dtype=np.float64)
    h, w = edge_array.shape

    # Compare edge density in center quadrant vs border strip
    cx, cy = w // 4, h // 4
    center = edge_array[cy:3*cy, cx:3*cx]
    border_top = edge_array[:cy, :]
    border_bottom = edge_array[3*cy:, :]
    border_left = edge_array[:, :cx]
    border_right = edge_array[:, 3*cx:]

    center_density = center.mean()
    border_density = np.mean([
        border_top.mean(), border_bottom.mean(),
        border_left.mean(), border_right.mean(),
    ])

    if center_density + border_density < 1:
        return 50.0

    ratio = center_density / max(center_density + border_density, 1)
    return min(100, ratio * 150)


def _score_color_separation(img_array: np.ndarray) -> float:
    """Score how distinct the dominant colors are."""
    from sklearn.cluster import KMeans

    pixels = img_array.reshape(-1, 3)
    # Subsample for speed
    if len(pixels) > 10000:
        indices = np.random.RandomState(42).choice(len(pixels), 10000, replace=False)
        pixels = pixels[indices]

    # Cluster into 8 representative colors
    kmeans = KMeans(n_clusters=8, random_state=42, n_init=3, max_iter=100)
    kmeans.fit(pixels)
    centers = kmeans.cluster_centers_

    # Measure average pairwise distance between cluster centers
    n = len(centers)
    total_dist = 0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            total_dist += np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
            count += 1

    avg_dist = total_dist / max(count, 1)
    # Normalize: avg_dist of ~150 = great, ~50 = poor
    return min(100, (avg_dist / 150) * 100)


def _score_contrast(img_array: np.ndarray) -> float:
    """Score contrast via luminance standard deviation."""
    # Convert to luminance
    luminance = (
        0.299 * img_array[:, :, 0] +
        0.587 * img_array[:, :, 1] +
        0.114 * img_array[:, :, 2]
    )
    std = luminance.std()
    # Normalize: std of ~60 = great, ~15 = poor
    return min(100, (std / 60) * 100)


def _score_background_simplicity(img_array: np.ndarray) -> float:
    """Score how simple/uniform the background is."""
    h, w, _ = img_array.shape
    # Sample the border regions
    border_size = max(1, min(h, w) // 10)
    border_pixels = np.concatenate([
        img_array[:border_size, :].reshape(-1, 3),
        img_array[-border_size:, :].reshape(-1, 3),
        img_array[:, :border_size].reshape(-1, 3),
        img_array[:, -border_size:].reshape(-1, 3),
    ])
    # Lower std = simpler background
    std = border_pixels.std(axis=0).mean()
    simplicity = max(0, 100 - std * 1.5)
    return simplicity


def _score_detail_density(image: Image.Image) -> float:
    """Score how much fine detail the image has."""
    # Resize to standard size for consistent measurement
    small = image.resize((200, 200), Image.LANCZOS).convert("L")
    edges = small.filter(ImageFilter.FIND_EDGES)
    edge_array = np.array(edges, dtype=np.float64)
    # Higher mean = more detail
    return min(100, edge_array.mean() * 3)
