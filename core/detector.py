"""
Hybrid Fractal-YOLO Vehicle Detection Engine.
Combines geometric/deep object bounding proposals with Fractal Complexity Filtering
to eliminate background false positives (e.g., foliage, road textures, shadows).
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import numpy as np
from PIL import Image

from .fractal_features import extract_roi_fractal_features


@dataclass
class DetectionBox:
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    class_name: str
    fractal_dimension: float
    lacunarity: float
    is_valid_vehicle: bool


class HybridVehicleDetector:
    def __init__(
        self,
        min_area: int = 400,
        max_area: int = 50000,
        df_min: float = 1.05,
        df_max: float = 1.60,
        max_lacunarity: float = 4.5,
        confidence_threshold: float = 0.50
    ):
        self.min_area = min_area
        self.max_area = max_area
        self.df_min = df_min
        self.df_max = df_max
        self.max_lacunarity = max_lacunarity
        self.confidence_threshold = confidence_threshold

    def generate_proposals(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Generates vehicle candidate bounding boxes using gradient saliency and intensity contrast.
        """
        h, w = frame.shape[:2]
        gray = frame if frame.ndim == 2 else np.mean(frame, axis=2).astype(np.uint8)

        # Gradient magnitude
        gy, gx = np.gradient(gray.astype(np.float32))
        grad = np.sqrt(gx**2 + gy**2)
        thresh = np.percentile(grad, 80)
        binary = (grad > thresh).astype(np.uint8)

        proposals = []
        # Multi-scale sliding window search for candidate clusters
        step = 32
        for win_h, win_w in [(48, 64), (64, 96), (80, 128)]:
            for y in range(0, h - win_h, step):
                for x in range(0, w - win_w, step):
                    patch_bin = binary[y : y + win_h, x : x + win_w]
                    density = np.mean(patch_bin)
                    if 0.12 <= density <= 0.55:
                        conf = float(density * 1.8)
                        proposals.append((x, y, x + win_w, y + win_h, min(0.99, conf)))

        # Non-maximum suppression (NMS)
        return self._apply_nms(proposals, iou_thresh=0.35)

    def _apply_nms(
        self,
        boxes: List[Tuple[int, int, int, int, float]],
        iou_thresh: float = 0.35
    ) -> List[Tuple[int, int, int, int, float]]:
        if not boxes:
            return []

        boxes_sorted = sorted(boxes, key=lambda b: b[4], reverse=True)
        keep = []

        while boxes_sorted:
            curr = boxes_sorted.pop(0)
            keep.append(curr)
            filtered = []
            for b in boxes_sorted:
                # Compute IoU
                ix1 = max(curr[0], b[0])
                iy1 = max(curr[1], b[1])
                ix2 = min(curr[2], b[2])
                iy2 = min(curr[3], b[3])
                inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
                area1 = (curr[2] - curr[0]) * (curr[3] - curr[1])
                area2 = (b[2] - b[0]) * (b[3] - b[1])
                union = area1 + area2 - inter
                iou = inter / union if union > 0 else 0.0
                if iou < iou_thresh:
                    filtered.append(b)
            boxes_sorted = filtered

        return keep

    def detect(self, frame: np.ndarray) -> List[DetectionBox]:
        """
        Runs hybrid detection on a frame:
        1. Propose candidate boxes
        2. Extract fractal dimension and lacunarity for each candidate
        3. Filter out false positives (foliage/shadows with irregular/extreme fractal complexity)
        """
        gray = frame if frame.ndim == 2 else np.mean(frame, axis=2).astype(np.uint8)
        proposals = self.generate_proposals(frame)

        results = []
        for x1, y1, x2, y2, conf in proposals:
            patch = gray[y1:y2, x1:x2]
            if patch.size == 0:
                continue

            feats = extract_roi_fractal_features(patch)
            df = feats["fractal_dimension"]
            lac = feats["lacunarity"]

            # Vehicle validation rule:
            # Man-made vehicles have regular geometric structures (df within [df_min, df_max])
            # and controlled lacunarity, whereas random foliage/shadows show excessive/irregular fractal dimensions
            is_valid = (
                (self.df_min <= df <= self.df_max)
                and (lac <= self.max_lacunarity)
                and (conf >= self.confidence_threshold)
            )

            # Class determination based on aspect ratio
            aspect = (x2 - x1) / float(y2 - y1)
            cls_name = "truck_bus" if aspect > 1.6 else "car"

            results.append(
                DetectionBox(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    confidence=conf,
                    class_name=cls_name,
                    fractal_dimension=df,
                    lacunarity=lac,
                    is_valid_vehicle=is_valid,
                )
            )

        return results
