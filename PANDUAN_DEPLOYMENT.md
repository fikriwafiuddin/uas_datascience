# Panduan Deployment ke PythonAnywhere

## 📋 Ketentuan Tugas yang Terpenuhi

| Ketentuan | Status | Keterangan |
|-----------|--------|------------|
| **b.** Membuat model prediksi menggunakan Regression | ✅ | Model regresi linier dengan koefisien dan intercept |
| **c.** Menunjukkan persamaan regresi | ✅ | Persamaan ditampilkan di halaman web |
| **d.** Halaman web menggunakan Flask | ✅ | Aplikasi Flask sudah siap |
| **e.** Menampilkan nilai prediksi | ✅ | Form input dan hasil prediksi tersedia |

---

## 🚀 Langkah-langkah Deployment ke PythonAnywhere

### 1. Buat Akun PythonAnywhere
- Kunjungi [www.pythonanywhere.com](https://www.pythonanywhere.com)
- Sign up untuk akun gratis (Beginner account)

### 2. Upload File Project

**Opsi A: Menggunakan PythonAnywhere Dashboard**
1. Login ke PythonAnywhere
2. Go to **Files**
3. Buat folder baru `/home/username/mysite/padi_prediction/`
4. Upload file-file berikut:
   - `app.py`
   - `flask_app.py`
   - `templates/index.html`

**Opsi B: Menggunakan Git (Recommended)**
1. Push project ke GitHub
2. Di PythonAnywhere, gunakan Bash console:
   ```bash
   cd $HOME
   git clone https://github.com/username/repo.git mysite
   ```

### 3. Install Dependencies

1. Buka **Bash console** di PythonAnywhere
2. Navigate ke project folder:
   ```bash
   cd $HOME/mysite
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

### 4. Konfigurasi WSGI

1. Go to **Web** tab
2. Klik **Add a new web app**
3. Pilih **Manual Configuration**
4. Pilih Python versi (rekomendasi: Python 3.10)
5. Di **Code** section, cari **WSGI configuration file**
6. Edit file `/var/www/username_pythonanywhere_com_wsgi.py`:
   ```python
   import sys
   project_home = '/home/username/mysite'
   if project_home not in sys.path:
       sys.path = [project_home] + sys.path

   from flask_app import application as application
   ```

### 5. Konfigurasi Virtual Environment

1. Di **Web** tab, scrol ke **Virtualenv**
2. Set path: `/home/username/mysite`
3. Install dependencies di virtualenv:
   ```bash
   workon mysitename
   pip install -r requirements.txt
   ```

### 6. Reload Web App

1. Di **Web** tab, scroll ke atas
2. Klik **Reload** button

### 7. Test Website

Buka website Anda: `http://username.pythonanywhere.com`

---

## 📁 Struktur Project

```
padi_prediction/
├── app.py                    # Main Flask application
├── flask_app.py              # WSGI entry point untuk PythonAnywhere
├── requirements.txt          # Python dependencies (Flask, numpy, scikit-learn)
├── templates/
│   ├── index.html           # Halaman prediksi padi (model fixed)
│   └── custom_regression.html  # Halaman regresi linier berganda custom
├── uas.ipynb                # Jupyter notebook training model
└── PANDUAN_DEPLOYMENT.md    # File ini
```

---

## 🧮 Model Regression

### Persamaan Regresi
```
y = 5.56836114 × Luas Panen (ha) + 7492.31789 × Produktivitas (ku/ha) - 420125.065542602
```

### Parameter
| Parameter | Nilai | Keterangan |
|-----------|-------|------------|
| Koefisien Luas Panen | 5.56836114 | Kontribusi per hektar |
| Koefisien Produktivitas | 7492.31789 | Kontribusi per ku/ha |
| Intercept | -420125.065542602 | Konstanta dasar |

---

## 🎯 Contoh Prediksi

| Luas Panen (ha) | Produktivitas (ku/ha) | Prediksi Produksi (ton) |
|-----------------|----------------------|-------------------------|
| 254287.38 | 55.22 | 1,409,564.69 |
| 101580.30 | 32.56 | 389,460.60 |
| 406109.49 | 51.40 | 2,087,474.15 |

---

## 📝 Screenshots yang Perlu Ditambahkan ke Laporan

1. Screenshot halaman web (tampilan awal)
2. Screenshot form dengan input data
3. Screenshot hasil prediksi
4. Screenshot dashboard PythonAnywhere

---

## ⚠️ Tips Deployment

1. **Free account limitations**:
   - Website akan "sleep" jika tidak ada aktivitas
   - Loading pertama mungkin lambat (±30 detik)

2. **Untuk production**:
   - Set `debug=False` di `app.py`
   - Gunakan environment variables untuk sensitive data

3. **Troubleshooting**:
   - Cek error log di PythonAnywhere Web tab
   - Pastikan semua dependencies terinstall
   - Verify WSGI configuration path benar

---

## 🔧 Cara Run Lokal (untuk testing)

```bash
# Install dependencies
pip install -r requirements.txt

# Run aplikasi
python app.py

# Buka browser ke: http://localhost:5000
```

---

## 🆕 Fitur Regresi Linier Berganda Custom

Aplikasi juga dilengkapi dengan fitur **Upload File** untuk regresi linier berganda. Fitur ini memungkinkan pengguna untuk:

1. **Upload File CSV/Excel** - Pengguna mengupload file data yang sudah ada
2. **Pilih Kolom Variabel** - Sistem membaca kolom dan user memilih X1, X2, ..., Y dari dropdown
3. **Melatih Model** - Sistem akan menghitung koefisien dan intercept secara otomatis
4. **Lihat Persamaan Regresi** - Persamaan regresi ditampilkan lengkap dengan koefisien
5. **Lakukan Prediksi** - Gunakan model yang sudah dilatih untuk prediksi data baru

### Cara Menggunakan Fitur Custom Regression

1. Buka halaman: `http://localhost:5000/custom-regression`
2. **Upload File**: Klik area upload dan pilih file CSV/Excel
3. **Preview Data**: Sistem menampilkan 5 baris pertama data
4. **Pilih Variabel**:
   - Centang kolom untuk variabel X (bisa lebih dari 1)
   - Pilih 1 kolom untuk variabel Y (target)
5. Klik "Latih Model Regresi"
6. Setelah model dilatih, persamaan regresi dan statistik ditampilkan
7. Input nilai untuk prediksi di form yang tersedia
8. Klik "Prediksi" untuk melihat hasil

### Format File yang Didukung

- **CSV** (.csv) - Comma Separated Values
- **Excel** (.xlsx, .xls) - Microsoft Excel

### Contoh File CSV

```csv
Provinsi,Luas Panen (ha),Produktivitas (ku/ha),Produksi (ton)
ACEH,254287.38,55.22,1404234.82
SUMATERA UTARA,406109.49,51.40,2087474.15
SUMATERA BARAT,300564.77,49.32,1482468.79
RIAU,51914.14,39.68,205972.55
JAMBI,61236.64,45.06,275941.45
```

**Pemilihan Variabel:**
- X (Checkbox): Luas Panen (ha), Produktivitas (ku/ha)
- Y (Dropdown): Produksi (ton)

### Contoh Penggunaan Lain

Fitur ini dapat digunakan untuk berbagai jenis data, bukan hanya produksi padi:

| Aplikasi | X1 | X2 | Y |
|----------|----|----|---|
| Penjualan | Promosi (Rp) | Harga (Rp) | Penjualan (unit) |
| Real Estate | Luas (m²) | Jumlah Kamar | Harga (jt Rp) |
| Kesehatan | Berat (kg) | Tinggi (cm) | BMI |
| Akademik | Waktu Belajar (jam) | Kehadiran (%) | Nilai Ujian |
