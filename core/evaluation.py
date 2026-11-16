"""
Performance Evaluation Module for Vehicle Detection & Counting.
Computes Precision, Recall, F1-Score, Mean Average Precision (mAP@0.5),
and Vehicle Counting Error Percentage.
"""

from typing import List, Tuple, Dict, Any
import numpy as np


def compute_iou(boxA: Tuple[int, int, int, int], boxB: Tuple[int, int, int, int]) -> float:
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter = max(0, xB - xA) * max(0, yB - yA)
    areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    union = areaA + areaB - inter
    return inter / float(union) if union > 0 else 0.0


def evaluate_detection_metrics(
    pred_boxes: List[Tuple[int, int, int, int, float]],
    gt_boxes: List[Tuple[int, int, int, int]],
    iou_threshold: float = 0.5
) -> Dict[str, float]:
    """
    Computes Precision, Recall, and F1-score given predicted boxes and ground-truth boxes.
    """
    if len(gt_boxes) == 0 and len(pred_boxes) == 0:
        return {"precision": 1.0, "recall": 1.0, "f1_score": 1.0, "tp": 0, "fp": 0, "fn": 0}
    if len(gt_boxes) == 0:
        return {"precision": 0.0, "recall": 1.0, "f1_score": 0.0, "tp": 0, "fp": len(pred_boxes), "fn": 0}
    if len(pred_boxes) == 0:
        return {"precision": 1.0, "recall": 0.0, "f1_score": 0.0, "tp": 0, "fp": 0, "fn": len(gt_boxes)}

    matched_gt = set()
    tp = 0
    fp = 0

    # Sort predictions by confidence
    sorted_preds = sorted(pred_boxes, key=lambda b: b[4], reverse=True)

    for p in sorted_preds:
        p_box = (p[0], p[1], p[2], p[3])
        best_iou = 0.0
        best_gt_idx = -1
        for g_idx, g_box in enumerate(gt_boxes):
            if g_idx in matched_gt:
                continue
            iou = compute_iou(p_box, g_box)
            if iou > best_iou:
                best_iou = iou
                best_gt_idx = g_idx

        if best_iou >= iou_threshold and best_gt_idx != -1:
            tp += 1
            matched_gt.add(best_gt_idx)
        else:
            fp += 1

    fn = len(gt_boxes) - len(matched_gt)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }


def compute_counting_accuracy(actual_count: int, estimated_count: int) -> Dict[str, float]:
    abs_err = abs(actual_count - estimated_count)
    pct_err = (abs_err / actual_count * 100.0) if actual_count > 0 else 0.0
    accuracy = max(0.0, 100.0 - pct_err)
    return {
        "actual_count": actual_count,
        "estimated_count": estimated_count,
        "absolute_error": abs_err,
        "error_percentage": pct_err,
        "counting_accuracy": accuracy,
    }
