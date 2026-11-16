"""
CLI for Hybrid Fractal and YOLO Vehicle Detection Suite.
"""

import argparse
import sys
import os
import numpy as np
from PIL import Image

from core.detector import HybridVehicleDetector
from core.tracker import TrafficTracker
from core.evaluation import evaluate_detection_metrics, compute_counting_accuracy


def cmd_detect(args):
    img = Image.open(args.input).convert("RGB")
    arr = np.array(img)
    detector = HybridVehicleDetector()
    dets = detector.detect(arr)

    valid_dets = [d for d in dets if d.is_valid_vehicle]
    print(f"Hasil Deteksi: {len(valid_dets)} kendaraan terdeteksi (dari {len(dets)} kandidat ROI)")
    for i, d in enumerate(valid_dets):
        print(f"  [{i+1}] {d.class_name.upper()} di ({d.x1},{d.y1})-({d.x2},{d.y2}) | DF: {d.fractal_dimension:.2f} | Lac: {d.lacunarity:.2f} | Conf: {d.confidence:.2f}")


def cmd_evaluate(args):
    from sample_data.generate_traffic import generate_traffic_scene
    frame_path, gt = generate_traffic_scene()
    img = Image.open(frame_path).convert("RGB")
    arr = np.array(img)

    detector = HybridVehicleDetector()
    dets = detector.detect(arr)
    valid_dets = [d for d in dets if d.is_valid_vehicle]
    preds = [(d.x1, d.y1, d.x2, d.y2, d.confidence) for d in valid_dets]

    metrics = evaluate_detection_metrics(preds, gt, iou_threshold=0.4)
    counting = compute_counting_accuracy(len(gt), len(valid_dets))

    print("\n" + "=" * 50)
    print("HASIL EVALUASI HYBRID FRACTAL-YOLO DETECTOR")
    print("=" * 50)
    print(f"Ground Truth Vehicles : {len(gt)}")
    print(f"Predicted Vehicles    : {len(valid_dets)}")
    print(f"True Positives (TP)   : {metrics['tp']}")
    print(f"False Positives (FP)  : {metrics['fp']}")
    print(f"False Negatives (FN)  : {metrics['fn']}")
    print(f"Precision             : {metrics['precision']*100:.2f}%")
    print(f"Recall                : {metrics['recall']*100:.2f}%")
    print(f"F1-Score              : {metrics['f1_score']*100:.2f}%")
    print(f"Counting Accuracy     : {counting['counting_accuracy']:.2f}%")
    print("=" * 50 + "\n")


def cmd_gui(args):
    from gui.app import launch_gui
    launch_gui()


def main():
    parser = argparse.ArgumentParser(description="Hybrid Fractal-YOLO Vehicle Detection")
    sub = parser.add_subparsers(dest="command")

    p_det = sub.add_parser("detect", help="Run detection on image")
    p_det.add_argument("input", help="Input image file")

    sub.add_parser("evaluate", help="Run evaluation on test scene")
    sub.add_parser("gui", help="Launch interactive traffic monitor GUI")

    args = parser.parse_args()
    if args.command == "detect":
        cmd_detect(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "gui":
        cmd_gui(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
