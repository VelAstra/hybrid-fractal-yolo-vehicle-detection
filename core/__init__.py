"""
Core Modules for Hybrid Fractal and YOLO Vehicle Detection Suite.
"""

from .fractal_features import compute_box_counting_dimension, compute_lacunarity, extract_roi_fractal_features
from .detector import HybridVehicleDetector, DetectionBox
from .tracker import TrafficTracker, TrackedVehicle
from .evaluation import evaluate_detection_metrics, compute_counting_accuracy

__all__ = [
    "compute_box_counting_dimension",
    "compute_lacunarity",
    "extract_roi_fractal_features",
    "HybridVehicleDetector",
    "DetectionBox",
    "TrafficTracker",
    "TrackedVehicle",
    "evaluate_detection_metrics",
    "compute_counting_accuracy",
]
