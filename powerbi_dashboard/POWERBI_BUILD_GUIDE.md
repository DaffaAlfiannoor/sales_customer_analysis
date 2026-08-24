# Panduan Membangun Dashboard Power BI — Online Retail Analysis

Panduan ini memandu Anda membangun dashboard 4 halaman di **Power BI Desktop**
menggunakan data dari folder `powerbi_data/`. Estimasi waktu: ±15–20 menit.

## Prasyarat

1. **Power BI Desktop** (gratis) — install via Microsoft Store atau
   <https://powerbi.microsoft.com/desktop>
2. Folder `powerbi_data/` berisi 7 file CSV (jangan dipindah/di-rename)
3. File pendukung di folder `powerbi_dashboard/`:
   - `dax_measures.txt` — semua rumus DAX siap copy-paste
   - `theme.json` — tema warna untuk diimpor

---

## Langkah 1 — Import Data

1. Buka Power BI Desktop → **Home > Get Data > Text/CSV**
2. Import satu per satu (pilih **Transform Data** dulu untuk cek tipe, lalu
   **Close & Apply**) — ATAU pilih langsung **Load** lalu perbaiki tipe di
   Power Query:

| Tabel | Kolom penting | Tipe yang benar |
|---|---|---|
| FactSales | InvoiceNo, StockCode, Description | Text |
| | Quantity, CustomerID, DateKey | Whole Number |
| | UnitPrice, TotalPrice | Decimal Number |
| | InvoiceDate | Date/Time |
| DimCustomer | CustomerID, R/F/M_score | Whole Number |
| | Recency, Frequency | Whole Number |
| | Monetary | Decimal Number |
| | Segment, ClusterSegment | Text |
| DimProduct | StockCode, ProductName | Text |
| DimCountry | Country | Text |
| DimDate | DateKey, Year, Month, Quarter | Whole Number |
| | Date | Date |
| | MonthName | Text |
| DimCohortCLV | CustomerID, Orders, Lifespan | Whole Number |
| | Total, AOV, PurchaseFreq, CLV | Decimal Number |
| | Cohort | Text |
| CohortRetention_long | CohortIndex | Whole Number |
| | Retention | Decimal Number |

> **Catatan**: `YearMonth` (FactSales) dan `Cohort` tetap **Text** agar urut
> kronologis saat dipakai sebagai sumbu.

---

## Langkah 2 — Buat Relasi Antar Tabel

Buka **Model view**, pastikan relasi berikut (biasanya auto-detect). Jika tidak,
drag kolomnya manual:

```
DimDate ──1:*──► FactSales ◄──* :1── DimProduct
   │                 │  ▲
   │                 │  │            DimCountry ──1:*──► FactSales[Country]
   │                 │  │
DimCustomer ──1:1──► DimCohortCLV      (CohortRetention_long: tanpa relasi)
```

| Dari (1) | Ke (*) | Kardinalitas | Cross-filter |
|---|---|---|---|
| `DimDate[DateKey]` | `FactSales[DateKey]` | One to Many | Single |
| `DimCustomer[CustomerID]` | `FactSales[CustomerID]` | One to Many | Single |
| `DimProduct[StockCode]` | `FactSales[StockCode]` | One to Many | Single |
| `DimCountry[Country]` | `FactSales[Country]` | One to Many | Single |
| `DimCustomer[CustomerID]` | `DimCohortCLV[CustomerID]` | One to One | Both |

Semua relasi **Active** = Yes.

---

## Langkah 3 — Mark as Date Table

1. Pilih tabel **DimDate** → ribbon **Table tools > Mark as date table**
2. Pilih kolom **Date**

Wajib agar measure `DATEADD` (Revenue MoM %) bekerja.

---

## Langkah 4 — Buat Measures

1. **Home > Enter Data** → beri nama `_Measures` → **Load** (tabel kosong)
2. Klik kanan `_Measures > New measure`, copy-paste rumus dari
   `dax_measures.txt` satu per satu (nama measure = teks sebelum tanda `=`)
3. Set format sesuai komentar di file tersebut (Currency / Percentage / dll.)
4. Opsional: kelompokkan via **Display folder** per kategori
5. Sembunyikan kolom kunci di FactSales dari report view (klik kanan >
   Hide in report view): `DateKey`, `StockCode`, `Description`, `CustomerID`

---

## Langkah 5 — Import Tema

**View > Themes > Browse for themes** → pilih `theme.json`.

---

## Langkah 6 — Bangun Halaman Dashboard

### Halaman 1 — Executive Overview

Jawab: total revenue, tren bulanan, kontribusi negara.

| # | Visual | Field | Setting |
|---|---|---|---|
| 1 | Card ×4 (baris atas) | `[Total Revenue]`, `[Total Orders]`, `[Total Customers]`, `[Avg Order Value (AOV)]` | Callout value besar |
| 2 | Card kecil ×2 | `[Revenue MoM %]`, `[Orders MoM %]` | Conditional formatting: merah jika negatif |
| 3 | Line chart | X: `DimDate[MonthName]` + `DimDate[Year]` (atau `FactSales[YearMonth]`) · Y: `[Total Revenue]` | Judul "Monthly Revenue Trend", data labels on |
| 4 | Clustered bar chart | Y: `DimCountry[Country]` · X: `[Total Revenue]` | Filter Top 10 by value; judul "Top 10 Countries by Revenue" |
| 5 | Donut chart | Legend: `FactSales[Country]` · Values: `[Total Revenue]` | Detail labels = percent; judul "Revenue Share by Country" |
| 6 | Slicer | `DimDate[Year]` | Style: Dropdown, kanan atas |
| 7 | Slicer | `DimCountry[Country]` | Style: Dropdown |

### Halaman 2 — Product Performance

| # | Visual | Field | Setting |
|---|---|---|---|
| 1 | Card ×3 | `[Active Products]`, `[Total Items Sold]`, `[Avg Items per Order]` | Baris atas |
| 2 | Bar chart Top 10 revenue | Y: `DimProduct[ProductName]` · X: `[Total Revenue]` | Filter Top 10; judul "Top 10 Products by Revenue" |
| 3 | Bar chart Top 10 units | Y: `DimProduct[ProductName]` · X: `[Total Items Sold]` | Filter Top 10; judul "Top 10 Products by Units Sold" |
| 4 | Bar chart Bottom 10 | Y: `DimProduct[ProductName]` · X: `[Total Revenue]` | Filter Bottom 10; judul "Bottom 10 Products by Revenue" |
| 5 | Table | ProductName, StockCode, `[Total Revenue]`, `[Total Items Sold]`, `[Avg Unit Price]` | Sort desc by revenue; enable search |
| 6 | Slicer | `DimProduct[ProductName]` | Style: List + Search |

### Halaman 3 — Customer & RFM

| # | Visual | Field | Setting |
|---|---|---|---|
| 1 | Card ×4 | `[Total Customers]`, `[Repeat Rate %]`, `[Champions Revenue %]`, `[At Risk Customers]` | Baris atas |
| 2 | Clustered column | X: `DimCustomer[Segment]` · Y: `COUNTROWS(DimCustomer)` (atau `[New Customers]`) | Judul "Customers by RFM Segment"; sort by value desc |
| 3 | Clustered column | X: `DimCustomer[Segment]` · Y: `[Total Revenue]` | Judul "Revenue by RFM Segment" |
| 4 | Scatter chart | X: `DimCustomer[Frequency]` · Y: `DimCustomer[Monetary]` · Size: `[Total CLV]` · Legend: `DimCustomer[ClusterSegment]` | Judul "Customer Clusters: Frequency vs Monetary" |
| 5 | Table Top 20 customers | CustomerID, Segment, Recency, Frequency, Monetary, RFM_score | Visual level filter Top 20 by Monetary |
| 6 | Slicer | `DimCustomer[ClusterSegment]` | Button style |

### Halaman 4 — Cohort & CLV

| # | Visual | Field | Setting |
|---|---|---|---|
| 1 | Card ×4 | `[Avg CLV]`, `[Avg Lifespan (Months)]`, `[Avg Retention M1]`, `[New Customers]` | Baris atas |
| 2 | Matrix (heatmap) | Rows: `CohortRetention_long[Cohort]` · Columns: `[CohortIndex]` · Values: AVERAGE of `[Retention]` | Format values as %. Conditional formatting > Background color > gradient min merah – max hijau. Kosongkan grand totals (Row/Column subtotals OFF) |
| 3 | Column chart | X: `DimCohortCLV[Cohort]` · Y: `[New Customers]` | Judul "New Customers per Cohort Month" |
| 4 | Line/column chart | X: `DimCohortCLV[Cohort]` · Y: `[Avg CLV]` | Judul "Average CLV by Cohort" |

> Heatmap retention memakai `CohortRetention_long.csv` apa adanya — jangan
> dihubungkan ke model, cukup drag field-nya langsung ke matrix.

---

## Langkah 7 — Sentuhan Akhir

1. **Rename tiap halaman** (double-click tab bawah):
   `Overview` · `Products` · `Customers` · `Cohorts & CLV`
2. **Sync slicers** Year/Country lintas halaman:
   View > Sync slicers → centang halaman tujuan
3. Cek interaksi antar visual (Format > Edit interactions) — default OK
4. **File > Save As** → `Online_Retail_Dashboard.pbix`
5. (Opsional) Publish ke Power BI Service: Home > Publish

---

## Troubleshooting

| Masalah | Solusi |
|---|---|
| `DATEADD` error / MoM kosong | Pastikan DimDate sudah *Mark as date table* (Langkah 3) |
| Relasi tidak terbentuk | Cek tipe kedua kolom sama (mis. dua-duanya Whole Number) |
| Angka retention aneh di matrix | Set agregasi ke **Average**, bukan Sum; matikan subtotals |
| Nilai besar tak terbaca | Format display units = Millions pada card revenue |
