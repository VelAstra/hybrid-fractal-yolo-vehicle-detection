"""
Fractal Feature Extraction Module for Vehicle Detection.
Computes Box-Counting Fractal Dimension (DF) and Lacunarity (Lambda)
to quantify structural texture complexity and filter false positive detections.
"""

from typing import Tuple, List
import numpy as np


def compute_box_counting_dimension(
    binary_image: np.ndarray,
    min_box_size: int = 2,
    max_box_size: int = None
) -> Tuple[float, List[int], List[int]]:
    """
    Computes Hausdorff-Besicovitch box-counting fractal dimension:
    D_F = - lim_{eps -> 0} (log N(eps) / log eps)
    """
    if binary_image.ndim != 2:
        raise ValueError("Binary image must be 2D")

    h, w = binary_image.shape
    p = min(h, w)
    if p < 4:
        return 0.0, [], []

    if max_box_size is None:
        max_box_size = p // 2

    # Power of 2 scales
    scales = []
    s = min_box_size
    while s <= max_box_size:
        scales.append(s)
        s *= 2

    if len(scales) < 2:
        return 1.0, [], []

    counts = []
    for s in scales:
        # Tiling and counting occupied boxes
        num_boxes_y = (h + s - 1) // s
        num_boxes_x = (w + s - 1) // s

        # Pad image to exact multiple
        pad_y = num_boxes_y * s - h
        pad_x = num_boxes_x * s - w
        padded = np.pad(binary_image, ((0, pad_y), (0, pad_x)), mode="constant", constant_values=0)

        # Reshape into boxes
        boxes = padded.reshape(num_boxes_y, s, num_boxes_x, s)
        occupied = np.any(boxes > 0, axis=(1, 3))
        counts.append(int(np.sum(occupied)))

    # Linear regression in log-log space
    log_inv_scales = np.log(1.0 / np.array(scales, dtype=np.float64))
    log_counts = np.log(np.maximum(1, np.array(counts, dtype=np.float64)))

    coeffs = np.polyfit(log_inv_scales, log_counts, 1)
    df = float(coeffs[0])
    return max(0.0, min(2.0, df)), scales, counts


def compute_lacunarity(image: np.ndarray, box_size: int = 4) -> float:
    """
    Computes Lacunarity (Lambda) representing the degree of structural gappiness/heterogeneity:
    Lambda = (Var(M) / Mean(M)^2) + 1
    """
    h, w = image.shape
    if h < box_size or w < box_size:
        return 1.0

    num_y = h // box_size
    num_x = w // box_size
    trimmed = image[: num_y * box_size, : num_x * box_size]

    boxes = trimmed.reshape(num_y, box_size, num_x, box_size)
    masses = np.sum(boxes, axis=(1, 3)).astype(np.float64)

    mean_mass = np.mean(masses)
    if mean_mass < 1e-6:
        return 1.0

    var_mass = np.var(masses)
    lacunarity = float((var_mass / (mean_mass ** 2)) + 1.0)
    return lacunarity


def extract_roi_fractal_features(roi_patch: np.ndarray) -> dict:
    """
    Extracts a feature vector for a candidate bounding box ROI:
    - Fractal Dimension DF
    - Lacunarity
    - Edge density
    """
    # Sobel gradient approximation for edges
    gy, gx = np.gradient(roi_patch.astype(np.float32))
    edge_mag = np.sqrt(gx ** 2 + gy ** 2)
    binary_edges = (edge_mag > (np.mean(edge_mag) + 0.5 * np.std(edge_mag))).astype(np.uint8)

    df, _, _ = compute_box_counting_dimension(binary_edges)
    lac = compute_lacunarity(edge_mag, box_size=4)
    edge_density = float(np.mean(binary_edges))

    return {
        "fractal_dimension": df,
        "lacunarity": lac,
        "edge_density": edge_density,
    }
