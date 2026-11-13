# MarketWatch-ID Lite

**Project type:** Independent portfolio project — equity EOD anomaly detection.

## Tujuan
Membangun dashboard sederhana untuk memeriksa data saham harian dan menandai perubahan harga atau lonjakan volume yang tidak biasa. Proyek ini ditujukan sebagai portofolio untuk posisi yang berkaitan dengan evaluasi sistem surveillance.

## MVP
1. Impor CSV historis / data sintetis yang memiliki izin penggunaan.
2. Validasi sederhana pada tanggal dan kolom OHLCV.
3. Deteksi anomali harga dan lonjakan volume berbasis aturan statistik.
4. Dashboard Streamlit: grafik, filter, dan tabel alert.
5. Pengujian otomatis dasar dengan kasus sintetis.

**Batasan:** Ini bukan sistem resmi IDX, bukan surveillance real-time, dan alert bukan bukti manipulasi pasar. Untuk demo publik gunakan data sintetis.

## Struktur folder
- `docs/` — scope proyek dan checklist.
- `data/demo/` — data sintetis aman untuk demo publik.
- `data/private/` — data penelitian lokal jika izin memadai; jangan unggah ke GitHub.
- `src/` — fungsi validasi dan aturan deteksi (akan diisi nanti).
- `app/` — dashboard Streamlit (akan diisi nanti).
- `tests/` — pengujian (akan diisi nanti).

## Status
Tahap 0: persiapan folder & VS Code. **Belum coding**.
