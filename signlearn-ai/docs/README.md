# SignLearn AI - Platform Pembelajaran BISINDO dengan AI

Program AI untuk belajar Bahasa Isyarat Indonesia (BISINDO) dengan teknologi Machine Learning dan MediaPipe untuk gesture recognition.

## 📋 Struktur Proyek

```
signlearn-ai/
├── backend/              # Backend API (Flask)
│   ├── app.py           # Main Flask application
│   ├── config.py        # Configuration settings
│   ├── requirements.txt  # Dependencies
│   ├── app/             # Application modules
│   ├── routes/          # API routes
│   │   ├── gestures.py  # Gesture endpoints
│   │   └── practice.py  # Practice endpoints
│   ├── database/        # Database layer
│   │   └── models.py    # SQLAlchemy models
│   ├── resources/       # Resource files
│   │   └── gestures/    # Gesture images
│   └── public/          # Static files
│
├── ai-service/          # AI/ML Service (Flask)
│   ├── app.py          # AI service Flask app
│   ├── model.py        # Gesture recognition model
│   ├── train.py        # Model training script
│   ├── requirements.txt # Dependencies
│   ├── model.pkl       # Trained model (generated)
│   ├── scaler.pkl      # Feature scaler (generated)
│   └── dataset/        # Training datasets
│
├── frontend/            # Frontend UI (HTML/CSS/JS)
│   ├── index.html      # Dashboard
│   ├── learn.html      # Learning page
│   ├── practice.html   # Practice page
│   ├── css/
│   │   └── style.css   # Styling
│   └── js/
│       ├── config.js        # API configuration
│       ├── dashboard.js     # Dashboard logic
│       ├── learn.js         # Learn page logic
│       └── practice.js      # Practice page logic
│
└── docs/               # Documentation
```

## 🗄️ Database Schema

### Gestures Table

```sql
CREATE TABLE gestures (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    image VARCHAR(255),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Practice Results Table

```sql
CREATE TABLE practice_results (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    gesture_id INTEGER NOT NULL,
    accuracy FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gesture_id) REFERENCES gestures(id)
);
```

## 🚀 Cara Setup dan Menjalankan

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Kamera web untuk practice mode

### 1. Setup Backend

```bash
# Navigate to backend folder
cd backend

# Install dependencies
pip install -r requirements.txt

# Run backend server
python app.py
```

Backend akan berjalan di `http://localhost:5000`

### 2. Setup AI Service

Buka terminal baru:

```bash
# Navigate to ai-service folder
cd ai-service

# Install dependencies
pip install -r requirements.txt

# Train model (opsional, untuk menggunakan data custom)
python train.py --sample

# Run AI service
python app.py
```

AI Service akan berjalan di `http://localhost:5001`

### 3. Setup Frontend

Buka file `frontend/index.html` di browser atau gunakan live server:

```bash
# Using Python
cd frontend
python -m http.server 8000

# Atau gunakan VS Code Live Server extension
```

Frontend akan berjalan di `http://localhost:8000`

## 📱 Fitur Utama

### 1. Dashboard

- Tampilan statistik pembelajaran
- Total praktik, akurasi rata-rata, gerakan yang benar
- Progress bar penguasaan gerakan

### 2. Pelajari Gerakan

- Daftar semua gerakan BISINDO
- Deskripsi dan tips untuk setiap gerakan
- Fitur pencarian gerakan
- Modal detail untuk setiap gerakan

### 3. Latihan Gerakan

- Practice mode dengan akses kamera
- AI real-time untuk mendeteksi gerakan
- Akurasi per gerakan
- Statistik sesi latihan
- Hasil tersimpan otomatis di database

## 🤖 Teknologi yang Digunakan

### Backend

- **Flask**: Web framework
- **SQLAlchemy**: ORM untuk database
- **SQLite**: Database
- **Flask-CORS**: Cross-Origin Resource Sharing

### AI Service

- **MediaPipe**: Hand pose detection
- **OpenCV**: Image processing
- **Scikit-learn**: Machine learning (Random Forest)
- **NumPy**: Numerical computing

### Frontend

- **HTML5**: Structure
- **CSS3**: Styling dan responsive design
- **Vanilla JavaScript**: Interactivity
- **Web APIs**: Camera access, fetch API

## 📊 API Endpoints

### Gestures

```
GET    /api/gestures              # Get all gestures (with pagination)
GET    /api/gestures/<id>         # Get specific gesture
POST   /api/gestures              # Create new gesture
PUT    /api/gestures/<id>         # Update gesture
DELETE /api/gestures/<id>         # Delete gesture
POST   /api/gestures/upload       # Upload gesture image
```

### Practice

```
GET    /api/practice/gestures     # Get random gestures for practice
POST   /api/practice/submit       # Submit practice result
GET    /api/practice/results/<user_id>  # Get user results
GET    /api/practice/stats/<user_id>    # Get user statistics
POST   /api/practice/predict      # Predict gesture from image
```

### AI Service

```
GET    /health                 # Health check
POST   /predict               # Predict gesture from image
POST   /train                 # Train model with images
GET    /labels                # Get gesture labels
POST   /add-label             # Add new gesture label
```

## 🎓 Gesture yang Disediakan

Default gestures dalam database:

1. **Halo** - Menyapa dengan melambaikan tangan
2. **Terima Kasih** - Mengucapkan terima kasih
3. **Tolong** - Meminta bantuan
4. **Maaf** - Minta maaf
5. **Ya** - Menjawab ya
6. **Tidak** - Menjawab tidak

## 🔧 Konfigurasi

### Backend Config (backend/config.py)

- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `UPLOAD_FOLDER`: Folder untuk menyimpan gesture images
- `MAX_CONTENT_LENGTH`: Ukuran file maksimal
- `SESSION_COOKIE_SECURE`: Cookie security settings

### Frontend Config (frontend/js/config.js)

- `API_BASE_URL`: Backend API URL (default: http://localhost:5000/api)
- `AI_SERVICE_URL`: AI Service URL (default: http://localhost:5001)

## 📈 User Data & Privacy

- **Tanpa Login**: Sistem tidak memerlukan login
- **Anonymous User ID**: User diidentifikasi dengan unique ID yang tersimpan di localStorage
- **Local Storage**: Data user ID disimpan di browser, bukan di server
- **Privacy**: Hanya results yang disimpan di database, tidak ada data pribadi

## 🚨 Troubleshooting

### Kamera tidak terbuka

- Pastikan aplikasi memiliki izin akses kamera
- Coba refresh halaman dan izinkan akses kamera
- Gunakan browser yang mendukung getUserMedia API

### AI Service tidak terkoneksi

```
Error: Cannot connect to AI service
```

- Pastikan AI Service sudah running di port 5001
- Check CORS settings di AI Service
- Verifikasi URL di config.js

### Database error

```
Error: SQLAlchemy database error
```

- Pastikan SQLite database file dapat ditulis
- Check folder permissions di backend
- Hapus database lama jika corrupted: `rm signlearn.db`

### Model tidak terlatih

```
Error: Model not trained
```

- Jalankan training script: `python train.py --sample`
- Tunggu hingga model.pkl dan scaler.pkl terbuat
- Restart AI Service

## 📝 Contoh Usage

### Create Gesture via API

```bash
curl -X POST http://localhost:5000/api/gestures \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Selamat",
    "image": "selamat.jpg",
    "description": "Gerakan untuk mengucapkan selamat"
  }'
```

### Submit Practice Result

```bash
curl -X POST http://localhost:5000/api/practice/submit \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "gesture_id": 1,
    "accuracy": 0.85
  }'
```

### Predict Gesture

```bash
curl -X POST http://localhost:5001/predict \
  -F "image=@gesture.jpg"
```

## 🎯 Pengembangan Lebih Lanjut

Fitur yang dapat ditambahkan:

- [ ] Video recording untuk setiap practice
- [ ] Leaderboard untuk kompetisi
- [ ] Audio feedback untuk guidance
- [ ] Mobile app version
- [ ] Multi-hand gesture recognition
- [ ] Real-time video stream analysis
- [ ] Export statistics to PDF
- [ ] Social sharing features
- [ ] Custom gesture creation
- [ ] Difficulty levels

## 📄 Lisensi

Proyek ini dibuat untuk keperluan pendidikan dan pembelajaran BISINDO.

## 👨‍💻 Author

SignLearn AI Team - 2024

---

**Catatan**: Untuk menggunakan fitur practice dengan akurasi terbaik, pastikan:

1. Pencahayaan ruangan cukup terang
2. Latar belakang kontras dengan warna tangan
3. Posisi kamera jelas melihat tangan
4. Gerakan dilakukan dengan jelas dan tidak terlalu cepat
