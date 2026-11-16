"""
Unit and Integration Tests for Hybrid Fractal-YOLO Vehicle Detection Suite.
"""

import unittest
import numpy as np

from core.fractal_features import compute_box_counting_dimension, compute_lacunarity, extract_roi_fractal_features
from core.detector import HybridVehicleDetector, DetectionBox
from core.tracker import TrafficTracker
from core.evaluation import evaluate_detection_metrics, compute_counting_accuracy, compute_iou


class TestHybridVehicleDetection(unittest.TestCase):

    def test_box_counting_dimension(self):
        # Solid square
        img = np.zeros((64, 64), dtype=np.uint8)
        img[16:48, 16:48] = 1
        df, scales, counts = compute_box_counting_dimension(img)
        self.assertGreater(df, 1.2)
        self.assertLessEqual(df, 2.0)

    def test_lacunarity(self):
        # Homogeneous image vs heterogeneous image
        homo = np.full((32, 32), 100, dtype=np.float32)
        hetero = np.random.uniform(0, 255, (32, 32)).astype(np.float32)
        lac_homo = compute_lacunarity(homo, box_size=4)
        lac_hetero = compute_lacunarity(hetero, box_size=4)
        self.assertEqual(lac_homo, 1.0)
        self.assertGreaterEqual(lac_hetero, 1.0)

    def test_detector_and_fractal_filtering(self):
        detector = HybridVehicleDetector()
        test_frame = np.full((200, 200, 3), 70, dtype=np.uint8)
        # Add a vehicle-like rectangle with edges
        test_frame[50:110, 50:110] = 200
        dets = detector.detect(test_frame)
        self.assertIsInstance(dets, list)

    def test_tracker_and_counter(self):
        tracker = TrafficTracker()
        det1 = DetectionBox(10, 20, 50, 60, 0.9, "car", 1.35, 1.2, True)
        # Frame 1
        tracks1 = tracker.update([det1], count_line_y=100)
        self.assertEqual(len(tracks1), 1)
        self.assertEqual(tracker.total_counted, 0)

        # Frame 2: Vehicle moves across line y=100
        det2 = DetectionBox(10, 95, 50, 135, 0.9, "car", 1.35, 1.2, True)
        tracks2 = tracker.update([det2], count_line_y=100)
        self.assertEqual(tracker.total_counted, 1)
        self.assertEqual(tracker.counts_by_class.get("car"), 1)

    def test_metrics(self):
        pred = [(10, 10, 50, 50, 0.9)]
        gt = [(10, 10, 50, 50)]
        res = evaluate_detection_metrics(pred, gt, iou_threshold=0.5)
        self.assertAlmostEqual(res["precision"], 1.0)
        self.assertAlmostEqual(res["recall"], 1.0)
        self.assertAlmostEqual(res["f1_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
