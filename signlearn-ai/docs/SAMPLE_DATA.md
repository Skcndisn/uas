# 📊 Penjelasan Sample Data - SignLearn AI

## Apa itu Sample Data?

**Sample data** adalah data dummy/percobaan yang dibuat otomatis untuk testing dan demo aplikasi. Ini bukan data real, tapi cukup untuk menjalankan training dan prediction.

## 📁 Struktur Sample Data

### Otomatis Dibuat (Synthetic)

```
Saat menjalankan: python train.py --sample

Training Data:
├── Gesture 1: Halo (10 synthetic images)
├── Gesture 2: Terima Kasih (10 synthetic images)
├── Gesture 3: Tolong (10 synthetic images)
├── Gesture 4: Maaf (10 synthetic images)
├── Gesture 5: Ya (10 synthetic images)
└── Gesture 6: Tidak (10 synthetic images)

Total: 60 synthetic images
```

### Hasil Training (Tersimpan):

```
ai-service/
├── model.pkl (430 KB) - Trained model
└── scaler.pkl (3.6 KB) - Feature scaler
```

## 🎯 Bagaimana Sample Data Bekerja?

### 1. **Pembuatan** (train.py)

```python
def create_sample_training_data():
    # Membuat 60 random images (480x640 pixels)
    # Setiap image: random color + green circle
    # Label: 6 gesture types, 10 per type
    # INI TIDAK REAL GESTURE - Hanya untuk demo
```

### 2. **Feature Extraction**

```
Synthetic Image → OpenCV Process → Features (126 values)
         ↓
Setiap image di-convert ke 126 numerical features
```

### 3. **Model Training**

```
60 Images + Labels → Random Forest → model.pkl
                        ↓
                  100 decision trees
                  Trained classifier
```

## 📊 File-File yang Dihasilkan

### model.pkl (430 KB)

- Binary file berisi trained Random Forest model
- 100 decision trees
- Parameter: n_estimators=100, max_depth=20
- Digunakan untuk prediction

### scaler.pkl (3.6 KB)

- Binary file berisi StandardScaler
- Menyimpan mean dan std dari training data
- Digunakan untuk scale input sebelum prediction

## 🔄 Workflow

### Training Phase (python train.py --sample)

```
Start
  ↓
Create 60 Synthetic Images
  ↓
Extract Features (126 per image)
  ↓
Scale Features (StandardScaler)
  ↓
Train Random Forest (100 trees)
  ↓
Save model.pkl & scaler.pkl
  ↓
Done ✓
```

### Prediction Phase (python app.py / practice.html)

```
User Upload Image
  ↓
Extract Features
  ↓
Load scaler.pkl → Scale features
  ↓
Load model.pkl → Predict
  ↓
Return: {gesture, accuracy, confidence}
```

## 📈 Performa Sample Model

```
Training Accuracy: ~90-95% (karena synthetic data, mudah di-classify)
Prediction Accuracy: Bergantung pada input image quality
Best Case: Jika input adalah image mirip synthetic
Worst Case: Real hand images (tidak ada hand detection)
```

## ⚠️ Limitasi Sample Data

1. **Tidak Real** - Data synthetic, bukan real gesture
2. **Akurasi Rendah** - Untuk production perlu real training data
3. **Waktu Latihan** - Hanya butuh beberapa detik
4. **Hand Detection** - MediaPipe tidak mendeteksi (karena tidak ada tangan)

## 🎓 Untuk Production (Real Data)

Jika ingin menggunakan real gesture data:

### 1. Siapkan Dataset

```
dataset/
├── Halo/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ... (minimal 20-50 images)
├── Terima Kasih/
│   └── ... (minimal 20-50 images)
├── Tolong/
│   └── ...
├── Maaf/
│   └── ...
├── Ya/
│   └── ...
└── Tidak/
    └── ...
```

### 2. Train dengan Real Data

```bash
cd ai-service
python train.py --dataset ./dataset
```

### 3. Hasil

```
Model akan:
- Detect real hand landmarks dari setiap image
- Extract 126 features per image
- Train classifier dengan real data
- Generate model.pkl yang lebih akurat
```

## 🔧 Testing Sample Model

### Via Command Line

```bash
cd ai-service
python -c "
from model import GestureRecognitionModel
model = GestureRecognitionModel()
result = model.predict('test_image.jpg')
print(result)
"
```

### Via Web API

```bash
curl -X POST http://localhost:5001/predict \
  -F "image=@test_gesture.jpg"
```

### Via Frontend

- Buka http://localhost:8000
- Klik "Latihan"
- Klik "Mulai Latihan"
- Capture frame dengan kamera
- AI akan predict gesture

## 💾 Reset / Retrain Model

### Hapus Model Lama

```bash
cd ai-service
del model.pkl
del scaler.pkl
```

### Retrain dengan Sample Data

```bash
python train.py --sample
```

### Atau dengan Custom Data

```bash
python train.py --dataset ./dataset
```

## 📊 Sample Data vs Real Data

| Aspek            | Sample Data        | Real Data              |
| ---------------- | ------------------ | ---------------------- |
| Sumber           | Synthetic (random) | Real photos            |
| Jumlah           | 60 images          | 200+ images            |
| Akurasi          | 90-95% (synthetic) | 75-90% (real gestures) |
| Waktu Train      | 1-2 detik          | 10-30 detik            |
| Hand Detection   | No                 | Yes (MediaPipe)        |
| Production Ready | ❌ No              | ✅ Yes                 |
| Testing          | ✅ Good            | ✅ Best                |

---

## ⚡ Quick Reference

**Untuk Demo/Testing**: Gunakan `--sample`

```bash
python train.py --sample
```

**Untuk Production**: Gunakan real dataset

```bash
python train.py --dataset ./dataset
```

**Check Model Status**:

```bash
curl http://localhost:5001/health
```

**Check Labels**:

```bash
curl http://localhost:5001/labels
```

---

**Catatan**: Sample data dibuat untuk membuktikan sistem berjalan. Untuk akurasi terbaik, gunakan real gesture images untuk training! 🤟
