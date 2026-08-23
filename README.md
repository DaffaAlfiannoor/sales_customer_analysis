# Sales & Customer Analysis - Online Retail

Analisis penjualan dan perilaku pelanggan menggunakan dataset **Online Retail** (541.909 transaksi, Desember 2010 - Desember 2011, 38 negara).

## 1. Persiapan Environment

Gunakan environment `py310-ml` (sudah berisi semua library yang dibutuhkan):

```bash
conda activate py310-ml
```

### Library yang Digunakan

| Library | Fungsi |
|---|---|
| `pandas` | Membaca data, manipulasi, agregasi |
| `numpy` | Operasi numerik |
| `matplotlib` | Visualisasi dasar |
| `seaborn` | Visualisasi statistik (heatmap, distplot) |
| `scipy` | Uji statistik |
| `scikit-learn` | K-Means clustering, StandardScaler, silhouette |
| `openpyxl` | Membaca file Excel (.xlsx) |

Import di notebook:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
```

## 2. Load Data

```python
df = pd.read_excel("Online Retail.xlsx", dtype={"CustomerID": "Int64"})
df.info()   # cek kolom, tipe data, missing value
df.head()   # cek 5 baris pertama
```

Struktur data:

| Kolom | Keterangan |
|---|---|
| InvoiceNo | Nomor invoice (awalan C = pembatalan) |
| StockCode | Kode produk |
| Description | Nama produk |
| Quantity | Jumlah item |
| InvoiceDate | Tanggal transaksi |
| UnitPrice | Harga satuan |
| CustomerID | ID pelanggan (NaN pada 135K baris) |
| Country | Negara pelanggan |

## 3. Langkah Pengerjaan

### Tahap 1 - Data Cleaning
1. Hapus baris dengan `CustomerID` NaN (tidak bisa dianalisis per customer)
2. Hapus transaksi pembatalan (InvoiceNo diawali huruf `C`)
3. Hapus `Quantity <= 0` (return) dan `UnitPrice <= 0`
4. Tambah kolom `TotalPrice = Quantity * UnitPrice`
5. Tambah kolom bulan/tahun dari `InvoiceDate`
6. Dokumentasikan jumlah data yang terbuang per langkah

### Tahap 2 - Exploratory Data Analysis (EDA)
1. Statistik deskriptif dan distribusi Quantity, UnitPrice, TotalPrice
2. Tren revenue per bulan (identifikasi musiman, peak November-Desember)
3. Top 10 produk berdasarkan unit terjual dan revenue
4. Top 10 negara berdasarkan revenue
5. Heatmap korelasi antar variabel

### Tahap 3 - RFM Analysis
1. Hitung **Recency**: selisih hari sejak transaksi terakhir (cutoff: 2011-12-09)
2. Hitung **Frequency**: jumlah transaksi per customer
3. Hitung **Monetary**: total belanja per customer
4. Beri skor kuartil 1-4 untuk tiap dimensi
5. Kategorikan segment: Champions, Loyal, Potential, At-risk, Lost

### Tahap 4 - K-Means Clustering
1. Standarisasi nilai RFM dengan `StandardScaler`
2. Tentukan jumlah cluster k dengan metode **elbow** dan **silhouette score**
3. Jalankan `KMeans` dan visualisasikan profil tiap cluster
4. Beri nama segment berdasarkan karakteristik cluster

### Tahap 5 - Cohort Analysis & CLV
1. Tentukan cohort berdasarkan bulan transaksi pertama customer
2. Hitung retention rate tiap cohort per bulan
3. Visualisasikan heatmap retention
4. Hitung churn rate dan Customer Lifetime Value (CLV) sederhana

### Tahap 6 - Output & Rekomendasi
1. Ekspor hasil ke folder `output/`:
   - `sales_monthly.csv` - rekap revenue bulanan
   - `rfm_scores.csv` - skor RFM per customer
   - `customer_segments.csv` - segmentasi customer
   - `cohort_retention.csv` - tabel retention
   - `insights_summary.xlsx` - ringkasan gabungan
2. Susun rekomendasi bisnis per segment customer

## 4. Pertanyaan Bisnis yang Dijawab

### Sales
- Berapa total revenue?
- Bagaimana perkembangan revenue setiap bulan?
- Bulan apa yang memiliki penjualan tertinggi?
- Negara mana yang memberikan revenue terbesar?

### Product
- Produk apa yang paling banyak terjual?
- Produk mana yang menghasilkan revenue terbesar?
- Produk mana yang memiliki performa buruk?

### Customer
- Berapa jumlah customer?
- Siapa customer dengan revenue terbesar?
- Berapa rata-rata nilai transaksi?
- Bagaimana pola pembelian customer?

### RFM
- Siapa customer paling loyal?
- Siapa customer bernilai tinggi?
- Siapa customer yang mulai tidak aktif?
- Siapa customer yang berpotensi hilang?

## 5. Catatan Penting Dataset

- UK mendominasi ±90% transaksi - bandingkan negara dengan average order value, bukan total saja
- Peak penjualan terjadi November-Desember 2011 (musim liburan)
- Ada outlier ekstrem (misal Quantity 80.000) - perlu dicek manual saat EDA