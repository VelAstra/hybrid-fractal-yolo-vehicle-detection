"""
Vehicle Tracking and Traffic Flow Counting Engine.
Uses IoU and Centroid association to track vehicles across CCTV frames
and counts directional line crossings.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import numpy as np

from .detector import DetectionBox


@dataclass
class TrackedVehicle:
    track_id: int
    class_name: str
    centroid: Tuple[float, float]
    bbox: Tuple[int, int, int, int]
    history: List[Tuple[float, float]]
    disappeared_count: int
    crossed_line: bool = False


class TrafficTracker:
    def __init__(self, max_disappeared: int = 5, distance_threshold: float = 120.0):
        self.max_disappeared = max_disappeared
        self.distance_threshold = distance_threshold
        self.next_id = 1
        self.tracks: Dict[int, TrackedVehicle] = {}
        self.total_counted = 0
        self.counts_by_class: Dict[str, int] = {}

    def update(
        self,
        detections: List[DetectionBox],
        count_line_y: Optional[int] = None
    ) -> List[TrackedVehicle]:
        valid_dets = [d for d in detections if d.is_valid_vehicle]

        # Extract current frame centroids
        det_centroids = []
        for d in valid_dets:
            cx = (d.x1 + d.x2) / 2.0
            cy = (d.y1 + d.y2) / 2.0
            det_centroids.append((cx, cy))

        if len(self.tracks) == 0:
            for i, d in enumerate(valid_dets):
                cx, cy = det_centroids[i]
                self.tracks[self.next_id] = TrackedVehicle(
                    track_id=self.next_id,
                    class_name=d.class_name,
                    centroid=(cx, cy),
                    bbox=(d.x1, d.y1, d.x2, d.y2),
                    history=[(cx, cy)],
                    disappeared_count=0,
                )
                self.next_id += 1
            return list(self.tracks.values())

        track_ids = list(self.tracks.keys())
        track_centroids = [self.tracks[tid].centroid for tid in track_ids]

        if len(det_centroids) > 0:
            # Pairwise distance matrix
            t_arr = np.array(track_centroids)
            d_arr = np.array(det_centroids)
            dists = np.linalg.norm(t_arr[:, np.newaxis] - d_arr[np.newaxis, :], axis=2)

            matched_tracks = set()
            matched_dets = set()

            # Greedy matching
            indices = np.argsort(dists, axis=None)
            for idx in indices:
                t_idx, d_idx = np.unravel_index(idx, dists.shape)
                if t_idx in matched_tracks or d_idx in matched_dets:
                    continue
                if dists[t_idx, d_idx] > self.distance_threshold:
                    break

                tid = track_ids[t_idx]
                d = valid_dets[d_idx]
                cx, cy = det_centroids[d_idx]

                prev_y = self.tracks[tid].centroid[1]
                self.tracks[tid].centroid = (cx, cy)
                self.tracks[tid].bbox = (d.x1, d.y1, d.x2, d.y2)
                self.tracks[tid].history.append((cx, cy))
                self.tracks[tid].disappeared_count = 0

                # Check line crossing
                if count_line_y is not None and not self.tracks[tid].crossed_line:
                    if (prev_y < count_line_y <= cy) or (prev_y > count_line_y >= cy):
                        self.tracks[tid].crossed_line = True
                        self.total_counted += 1
                        cls_name = self.tracks[tid].class_name
                        self.counts_by_class[cls_name] = self.counts_by_class.get(cls_name, 0) + 1

                matched_tracks.add(t_idx)
                matched_dets.add(d_idx)

            # Unmatched existing tracks
            for t_idx, tid in enumerate(track_ids):
                if t_idx not in matched_tracks:
                    self.tracks[tid].disappeared_count += 1

            # Unmatched new detections
            for d_idx, d in enumerate(valid_dets):
                if d_idx not in matched_dets:
                    cx, cy = det_centroids[d_idx]
                    self.tracks[self.next_id] = TrackedVehicle(
                        track_id=self.next_id,
                        class_name=d.class_name,
                        centroid=(cx, cy),
                        bbox=(d.x1, d.y1, d.x2, d.y2),
                        history=[(cx, cy)],
                        disappeared_count=0,
                    )
                    self.next_id += 1
        else:
            for tid in track_ids:
                self.tracks[tid].disappeared_count += 1

        # Prune expired tracks
        dead_tracks = [tid for tid, trk in self.tracks.items() if trk.disappeared_count > self.max_disappeared]
        for tid in dead_tracks:
            del self.tracks[tid]

        return list(self.tracks.values())
