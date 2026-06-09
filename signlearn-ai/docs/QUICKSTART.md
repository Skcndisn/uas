# Quick Start Guide - SignLearn AI

## ⚡ Panduan Cepat Untuk Menjalankan SignLearn AI

### Step 1: Persiapan Awal

1. Pastikan Python 3.8+ sudah terinstall
2. Clone/download folder signlearn-ai
3. Buka 3 terminal/command prompt

### Step 2: Jalankan Backend (Terminal 1)

```bash
cd signlearn-ai/backend
pip install -r requirements.txt
python app.py
```

**Output yang diharapkan:**

```
 * Running on http://127.0.0.1:5000
 * DEBUG mode is on
```

### Step 3: Jalankan AI Service (Terminal 2)

```bash
cd signlearn-ai/ai-service
pip install -r requirements.txt
python train.py --sample
python app.py
```

**Output yang diharapkan:**

```
 * Running on http://127.0.0.1:5001
 * Model loaded: model.pkl
```

### Step 4: Jalankan Frontend (Terminal 3)

```bash
cd signlearn-ai/frontend
python -m http.server 8000
```

**Output yang diharapkan:**

```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

### Step 5: Buka di Browser

Buka browser dan kunjungi:

```
http://localhost:8000
```

## ✅ Verifikasi Semua Service Berjalan

Buka di tab browser baru:

1. **Backend**: http://localhost:5000/health

   ```json
   { "status": "healthy", "service": "signlearn-backend" }
   ```

2. **AI Service**: http://localhost:5001/health

   ```json
   {
     "status": "healthy",
     "service": "signlearn-ai-service",
     "model_loaded": true
   }
   ```

3. **Frontend**: http://localhost:8000
   - Halaman dashboard akan terbuka

## 🎮 Cara Menggunakan

### Dashboard

- Lihat statistik pembelajaran Anda
- Pantau progres penguasaan gerakan

### Pelajari Gerakan

- Klik "Pelajari" di menu atas
- Browse semua gerakan BISINDO
- Klik gesture untuk melihat detail dan tips

### Latihan Gerakan

- Klik "Latihan" di menu atas
- Klik "Mulai Latihan"
- Izinkan akses kamera
- Lihat gerakan target di layar
- Tunjukkan gerakan di depan kamera
- Klik "Capture" untuk evaluasi
- AI akan memberikan skor akurasi

## 📊 Melihat Database

### Backend - SQLite Database

```bash
# Di folder backend
sqlite3 signlearn.db

# Lihat gestures
SELECT * FROM gestures;

# Lihat practice results
SELECT * FROM practice_results;

# Exit
.exit
```

## 🐛 Jika Ada Error

### Error: "Cannot GET /health"

- Pastikan terminal 1 (backend) masih running
- Restart backend server

### Error: "AI service error"

- Pastikan terminal 2 (AI service) masih running
- Restart AI service
- Verifikasi model sudah di-train: cek file `model.pkl`

### Error: "Cannot connect to AI service"

- Pastikan port 5001 tidak ter-block firewall
- Verifikasi AI service berjalan dengan `http://localhost:5001/health`

### Error: Kamera tidak bisa diakses

- Izinkan akses kamera untuk browser
- Coba refresh halaman
- Gunakan browser modern (Chrome, Firefox, Edge)

### Error: CORS error

- Pastikan semua services sudah running
- Check console browser (F12 > Console tab)
- Restart semua services

## 📱 Fitur yang Bisa Dicoba

1. **Dashboard** - Lihat statistik sebelum mulai
2. **Learn** - Pelajari gerakan-gerakan
3. **Practice** - Lakukan latihan dengan kamera
4. **Automatic Save** - Hasil latihan otomatis tersimpan

## 🎯 Tips Latihan Efektif

1. **Pencahayaan**: Pastikan ruangan cukup terang
2. **Jarak**: Posisi tangan ~30-60cm dari kamera
3. **Latar**: Gunakan latar belakang yang kontras
4. **Gerakan**: Gerakan jelas dan tidak terlalu cepat
5. **Konsistensi**: Latih secara rutin

## 🔧 Mengubah Port

Jika port sudah digunakan, ubah di:

**Backend** (backend/app.py, baris terakhir):

```python
app.run(debug=True, host='0.0.0.0', port=5002)  # Ubah dari 5000 ke 5002
```

**AI Service** (ai-service/app.py, baris terakhir):

```python
app.run(debug=True, host='0.0.0.0', port=5003)  # Ubah dari 5001 ke 5003
```

**Frontend** (terminal 3):

```bash
python -m http.server 8001  # Ubah dari 8000 ke 8001
```

Update config di `frontend/js/config.js`:

```javascript
const API_BASE_URL = "http://localhost:5002/api"; // Update
const AI_SERVICE_URL = "http://localhost:5003"; // Update
```

## 📞 Support

Jika masalah persisten:

1. Check internet connection
2. Restart semua terminals
3. Clear browser cache (Ctrl+Shift+Delete)
4. Coba di browser berbeda

---

**Selamat belajar BISINDO dengan SignLearn AI!** 🤟
