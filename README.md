# Hybrid Fractal and YOLO for Vehicle Detection Suite

> **Proyek Capstone 2**: Sistem Deteksi dan Penghitung Kendaraan Cerdas Berbasis Hybrid Fractal Complexity dan YOLO  
> **Program Studi**: S1 Ilmu Komputer / Informatika, FMIPA, Universitas Gadjah Mada  

---

## Ringkasan Proyek
Menggabungkan ekstraksi fitur kompleksitas fraktal (*Box-Counting Fractal Dimension* $D_F$ dan *Lacunarity* $\Lambda$) dengan usulan deteksi objek spasial untuk mendeteksi, melacak, dan menghitung kendaraan dari rekaman CCTV lalu lintas serta menyaring *false positive* akibat latar belakang alami (dedaunan dan bayangan jalan).

### Pembagian Tugas Tim 4 Mahasiswa
1. **Mahasiswa 1**: Preprocessing Video & Ekstraksi Frame CCTV.
2. **Mahasiswa 2**: Ekstraksi Fitur Dimensi Fraktal ($D_F$) dan Lakunaritas.
3. **Mahasiswa 3**: Mesin Detektor Hybrid & Algoritma Pelacak Kendaraan (*Traffic Tracker*).
4. **Mahasiswa 4**: Antarmuka Grafis (Tkinter GUI), Integrasi Sistem, & Evaluasi Metrik (mAP, Precision, Recall).

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
