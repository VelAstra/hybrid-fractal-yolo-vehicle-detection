"""
Interactive Traffic Vehicle Detection Dashboard.
Role: Rayhan Haldi Hermawan (GUI, Evaluation, & Integration).
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk, ImageDraw

from core.detector import HybridVehicleDetector
from core.tracker import TrafficTracker


class TrafficMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hybrid Fractal-YOLO Traffic Monitor & Vehicle Counter")
        self.geometry("1000x700")
        self.configure(bg="#0F172A")

        self.detector = HybridVehicleDetector()
        self.tracker = TrafficTracker()
        self.current_frame = None
        self.tk_image = None

        self._build_ui()
        sample = os.path.join(os.path.dirname(__file__), "..", "sample_data", "traffic_frame.png")
        if os.path.exists(sample):
            self.load_frame(os.path.abspath(sample))

    def _build_ui(self):
        header = tk.Frame(self, bg="#1E293B", height=60, padx=20)
        header.pack(fill=tk.X)
        tk.Label(header, text="HYBRID FRACTAL-YOLO TRAFFIC ANALYSIS", font=("Segoe UI", 14, "bold"), fg="#38BDF8", bg="#1E293B").pack(anchor="w", pady=(10, 0))
        tk.Label(header, text="Deteksi Kendaraan CCTV dengan Filter Kompleksitas Fraktal", font=("Segoe UI", 9), fg="#94A3B8", bg="#1E293B").pack(anchor="w")

        tools = tk.Frame(self, bg="#0F172A", padx=15, pady=10)
        tools.pack(fill=tk.X)
        ttk.Button(tools, text="Pilih Gambar/Frame...", command=self.on_browse).pack(side=tk.LEFT, padx=5)
        ttk.Button(tools, text="Jalankan Deteksi Fraktal", command=self.on_detect).pack(side=tk.LEFT, padx=5)

        # Center View
        self.canvas_lbl = tk.Label(self, bg="#020617")
        self.canvas_lbl.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Stats bar
        stats = tk.Frame(self, bg="#1E293B", padx=15, pady=8)
        stats.pack(fill=tk.X, side=tk.BOTTOM)
        self.lbl_stats = tk.Label(stats, text="Status: Siap.", font=("Segoe UI", 10), bg="#1E293B", fg="#F8FAFC")
        self.lbl_stats.pack(side=tk.LEFT)

    def load_frame(self, path):
        img = Image.open(path).convert("RGB")
        self.current_frame = np.array(img)
        self.render_image(img)

    def render_image(self, pil_img):
        resized = pil_img.resize((800, 450), Image.Resampling.BILINEAR)
        self.tk_image = ImageTk.PhotoImage(resized)
        self.canvas_lbl.config(image=self.tk_image)

    def on_browse(self):
        f = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if f:
            self.load_frame(f)

    def on_detect(self):
        if self.current_frame is None:
            return
        dets = self.detector.detect(self.current_frame)
        valid = [d for d in dets if d.is_valid_vehicle]

        # Annotate image
        img = Image.fromarray(self.current_frame)
        draw = ImageDraw.Draw(img)
        for d in valid:
            draw.rectangle([d.x1, d.y1, d.x2, d.y2], outline=(56, 189, 248), width=3)
            draw.text((d.x1 + 4, d.y1 + 4), f"{d.class_name} | DF:{d.fractal_dimension:.2f}", fill=(255, 255, 0))

        self.render_image(img)
        self.lbl_stats.config(text=f"Deteksi Selesai: {len(valid)} kendaraan terverifikasi fraktal.")


def launch_gui():
    app = TrafficMonitorApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
