# Panduan Database - SignLearn AI

## 📊 Schema Database SQLite

### 1. Gestures Table

Menyimpan data gerakan BISINDO yang tersedia.

```sql
CREATE TABLE gestures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    image VARCHAR(255),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Kolom:**

- `id`: Unique identifier untuk gesture
- `name`: Nama gerakan (unik)
- `image`: Path/URL gambar gesture
- `description`: Penjelasan gerakan
- `created_at`: Waktu pembuatan
- `updated_at`: Waktu update terakhir

**Contoh Data:**

```
id | name         | image           | description
1  | Halo         | halo.jpg        | Lambaikan tangan ke depan...
2  | Terima Kasih | terima_kasih.jpg| Tangan di dada...
```

### 2. Practice Results Table

Menyimpan hasil setiap latihan pengguna.

```sql
CREATE TABLE practice_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL,
    gesture_id INTEGER NOT NULL,
    accuracy FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gesture_id) REFERENCES gestures(id) ON DELETE CASCADE
);
```

**Kolom:**

- `id`: Unique identifier untuk hasil praktik
- `user_id`: Identifier user (anonymous)
- `gesture_id`: ID gesture yang dipraktikkan
- `accuracy`: Akurasi (0.0 - 1.0 atau 0 - 100%)
- `status`: Status hasil ('correct', 'partial', 'incorrect')
- `created_at`: Waktu praktik

**Contoh Data:**

```
id | user_id              | gesture_id | accuracy | status    | created_at
1  | user_123456789       | 1          | 0.92     | correct   | 2024-01-15 10:30:00
2  | user_123456789       | 2          | 0.65     | partial   | 2024-01-15 10:32:00
```

## 🔑 Relationships

```
gestures (1) ──── (Many) practice_results
```

- Satu gesture dapat memiliki banyak practice results
- Ketika gesture dihapus, semua practice results-nya juga dihapus (CASCADE)

## 📝 Query Contoh

### Melihat Semua Gesture

```sql
SELECT * FROM gestures ORDER BY created_at DESC;
```

### Melihat Practice Results untuk User Tertentu

```sql
SELECT pr.*, g.name as gesture_name
FROM practice_results pr
JOIN gestures g ON pr.gesture_id = g.id
WHERE pr.user_id = 'user_123456789'
ORDER BY pr.created_at DESC;
```

### Statistik Akurasi Per User

```sql
SELECT
    pr.user_id,
    COUNT(*) as total_practices,
    AVG(pr.accuracy) as average_accuracy,
    SUM(CASE WHEN pr.status = 'correct' THEN 1 ELSE 0 END) as correct_count,
    SUM(CASE WHEN pr.status = 'partial' THEN 1 ELSE 0 END) as partial_count,
    SUM(CASE WHEN pr.status = 'incorrect' THEN 1 ELSE 0 END) as incorrect_count
FROM practice_results pr
GROUP BY pr.user_id;
```

### Akurasi Rata-rata Per Gesture

```sql
SELECT
    g.name,
    COUNT(pr.id) as times_practiced,
    AVG(pr.accuracy) as average_accuracy,
    MAX(pr.accuracy) as best_accuracy,
    MIN(pr.accuracy) as worst_accuracy
FROM gestures g
LEFT JOIN practice_results pr ON g.id = pr.gesture_id
GROUP BY g.id, g.name
ORDER BY average_accuracy DESC;
```

### Gesture yang Paling Sering Dipraktikkan

```sql
SELECT
    g.name,
    COUNT(pr.id) as practice_count
FROM gestures g
JOIN practice_results pr ON g.id = pr.gesture_id
GROUP BY g.id
ORDER BY practice_count DESC
LIMIT 5;
```

### Practice Results Hari Ini

```sql
SELECT
    pr.user_id,
    g.name,
    pr.accuracy,
    pr.status,
    datetime(pr.created_at) as time
FROM practice_results pr
JOIN gestures g ON pr.gesture_id = g.id
WHERE date(pr.created_at) = date('now')
ORDER BY pr.created_at DESC;
```

## 🔄 Data Integrity

### Foreign Key Constraint

- Setiap `practice_results.gesture_id` harus refer ke `gestures.id` yang valid
- Jika gesture dihapus, practice results-nya juga dihapus otomatis

### Unique Constraint

- `gestures.name` harus unik (tidak boleh ada nama gesture yang sama)

### Not Null Constraint

- `gestures.name` wajib ada
- `practice_results.user_id` wajib ada
- `practice_results.gesture_id` wajib ada
- `practice_results.accuracy` wajib ada
- `practice_results.status` wajib ada

## 💾 Backup & Restore

### Backup Database

```bash
# Copy file database
cp signlearn.db signlearn.db.backup

# Atau export sebagai SQL
sqlite3 signlearn.db .dump > backup.sql
```

### Restore Database

```bash
# Restore dari backup
cp signlearn.db.backup signlearn.db

# Atau dari SQL dump
sqlite3 signlearn.db < backup.sql
```

## 🗑️ Cleanup & Maintenance

### Hapus Practice Results yang Lama

```sql
DELETE FROM practice_results
WHERE created_at < datetime('now', '-30 days');
```

### Optimize Database

```sql
VACUUM;
```

### Reset Database (HATI-HATI!)

```bash
# Hapus database dan restart aplikasi
rm signlearn.db

# Backend akan membuat database baru dengan data default
python app.py
```

## 📈 Database Growth

**Estimasi ukuran database:**

- Setiap gesture record: ~500 bytes
- Setiap practice result: ~200 bytes
- 6 gestures + 10,000 practice results ≈ 2 MB

## 🔐 Security Notes

1. **Anonymous Users**: User ID di-generate otomatis, tidak ada data pribadi
2. **No Passwords**: Sistem tidak menyimpan password atau data sensitif
3. **Local Database**: SQLite database tersimpan lokal di server
4. **CORS Protected**: API dilindungi dengan CORS headers

## 📊 Monitoring

### Monitor Database Size

```bash
ls -lh signlearn.db
```

### Check Database Integrity

```bash
sqlite3 signlearn.db "PRAGMA integrity_check;"
```

### Get Database Statistics

```bash
sqlite3 signlearn.db

sqlite> SELECT
    'gestures' as table_name,
    COUNT(*) as row_count
FROM gestures
UNION ALL
SELECT
    'practice_results',
    COUNT(*)
FROM practice_results;
```

---

Untuk informasi lebih lanjut, lihat dokumentasi SQLAlchemy di `backend/database/models.py`
