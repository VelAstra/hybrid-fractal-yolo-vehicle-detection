# Hybrid Fractal and YOLO for Vehicle Detection Suite

> **Proyek Capstone 2**: Sistem Deteksi dan Penghitung Kendaraan Cerdas Berbasis Hybrid Fractal Complexity dan YOLO  
> **Program Studi**: S1 Ilmu Komputer / Informatika, FMIPA, Universitas Gadjah Mada  
> **Anggota Tim Pengembang**:  
> - Aji Kusuma Putra (NIM: 22/503701/PA/21657)  
> - Rayhan Haldi Hermawan (NIM: 24/545406/PA/23176)  

---

## Ringkasan Proyek
Menggabungkan ekstraksi fitur kompleksitas fraktal (*Box-Counting Fractal Dimension* $D_F$ dan *Lacunarity* $\Lambda$) dengan usulan deteksi objek spasial untuk mendeteksi, melacak, dan menghitung kendaraan dari rekaman CCTV lalu lintas serta menyaring *false positive* akibat latar belakang alami (dedaunan dan bayangan jalan).

### Pembagian Tugas Tim (2 Mahasiswa)
1. **Aji Kusuma Putra** (`22/503701/PA/21657`): Video preprocessing, ekstraksi frame CCTV berkala, stabilisasi latar belakang, serta ekstraksi fitur dimensi fraktal box-counting dan lakunaritas tekstur ROI kendaraan. (Modul: `sample_data/generate_traffic.py`, `core/fractal_features.py`).
2. **Rayhan Haldi Hermawan** (`24/545406/PA/23176`): Mesin detektor hybrid, pelacakan multi-objek centroid tracking, garis batas virtual (virtual counting line), GUI Dashboard Tkinter, integrasi CLI, dan evaluasi metrik (mAP, Precision, Recall). (Modul: `core/detector.py`, `core/tracker.py`, `core/evaluation.py`, `gui/app.py`, `cli.py`).

---

## Cara Menjalankan

```bash
# Menjalankan deteksi pada citra sampel
python cli.py detect sample_data/traffic_frame.png

# Menjalankan evaluasi presisi dan akurasi penghitungan
python cli.py evaluate

# Menjalankan antarmuka grafis
python cli.py gui

# Menjalankan uji otomatis
python -m unittest discover tests
```
