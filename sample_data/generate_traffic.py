"""
Synthetic Traffic Video Frame Generator for Hybrid Fractal-YOLO Vehicle Detection.
Renders multi-lane highway scenes with vehicles, lane markings, and natural foliage.
"""

import os
from typing import List, Tuple
import numpy as np
from PIL import Image, ImageDraw


def generate_traffic_scene(
    width: int = 640,
    height: int = 360,
    vehicles_config: List[Tuple[int, int, int, int, str]] = None,
    filepath: str = "sample_data/traffic_frame.png"
) -> Tuple[str, List[Tuple[int, int, int, int]]]:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img = Image.new("RGB", (width, height), color=(50, 50, 50))
    draw = ImageDraw.Draw(img)

    # Road surface
    draw.rectangle([60, 0, width - 60, height], fill=(65, 68, 72))

    # Lane markings (dashed white lines)
    for x_lane in [200, 320, 440]:
        for y_dash in range(0, height, 40):
            draw.line([x_lane, y_dash, x_lane, y_dash + 20], fill=(240, 240, 240), width=3)

    # Sidewalk / Foliage on borders (fractal texture)
    rng = np.random.default_rng(101)
    for _ in range(80):
        # Left foliage
        bx = rng.integers(5, 55)
        by = rng.integers(10, height - 10)
        draw.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(30, 80, 30))
        # Right foliage
        bx = rng.integers(width - 55, width - 5)
        by = rng.integers(10, height - 10)
        draw.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(30, 80, 30))

    if vehicles_config is None:
        vehicles_config = [
            (100, 80, 160, 150, "car"),
            (220, 180, 290, 260, "car"),
            (350, 50, 430, 180, "truck_bus"),
        ]

    gt_boxes = []
    for x1, y1, x2, y2, vtype in vehicles_config:
        gt_boxes.append((x1, y1, x2, y2))
        color = (180, 40, 40) if vtype == "car" else (40, 100, 190)
        # Vehicle body
        draw.rectangle([x1, y1, x2, y2], fill=color, outline=(20, 20, 20), width=2)
        # Windshield
        w_h = (y2 - y1) // 4
        draw.rectangle([x1 + 6, y1 + w_h, x2 - 6, y1 + 2 * w_h], fill=(40, 40, 50))
        # Headlights / Taillights
        draw.rectangle([x1 + 4, y2 - 6, x1 + 12, y2 - 2], fill=(240, 200, 40))
        draw.rectangle([x2 - 12, y2 - 6, x2 - 4, y2 - 2], fill=(240, 200, 40))

    img.save(filepath)
    return filepath, gt_boxes


if __name__ == "__main__":
    p, b = generate_traffic_scene()
    print(f"Generated traffic frame: {p} with {len(b)} ground-truth vehicles")
