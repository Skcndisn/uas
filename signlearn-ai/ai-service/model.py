import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import joblib
import os
from PIL import Image
from skimage.feature import hog
from skimage.transform import resize as sk_resize

IMG_SIZE = (64, 64)

def extract_hog_features(image):
    """
    Extract HOG features from an image.
    image: numpy array (H, W, 3) RGB or (H, W) grayscale, OR PIL Image
    Returns: 1D numpy array of features
    """
    if isinstance(image, Image.Image):
        pil_img = image.convert('L')
    elif isinstance(image, np.ndarray):
        if image.ndim == 3:
            pil_img = Image.fromarray(image).convert('L')
        else:
            pil_img = Image.fromarray(image)
    else:
        raise ValueError(f"Unsupported image type: {type(image)}")

    pil_img = pil_img.resize(IMG_SIZE, Image.LANCZOS)
    arr = np.array(pil_img, dtype=np.float32) / 255.0

    feats = hog(
        arr,
        orientations=9,
        pixels_per_cell=(8, 8),
        cells_per_block=(2, 2),
        block_norm='L2-Hys',
        feature_vector=True
    )
    return feats


class GestureRecognitionModel:
    """BISINDO gesture recognition using HOG + SVM (no cv2/mediapipe required)"""

    def __init__(self, model_path='model.pkl', scaler_path='scaler.pkl'):
        self.model_path = model_path
        self.scaler_path = scaler_path

        self.gesture_labels = {i: chr(ord('A') + i) for i in range(26)}
        self.reverse_labels = {v: k for k, v in self.gesture_labels.items()}

        self.model = None
        self.scaler = None
        self.load_model()

    def extract_hand_features(self, image):
        """Public feature extraction used by predict."""
        try:
            feats = extract_hog_features(image)
            return feats.reshape(1, -1)
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return None

    def train_from_dataset(self, dataset_path):
        """
        Train directly from a dataset directory:
          dataset_path/A/img1.jpg ...
          dataset_path/B/img1.jpg ...
        """
        X, y = [], []
        letters = sorted(os.listdir(dataset_path))
        print(f"Found classes: {letters}")
        for letter in letters:
            letter_dir = os.path.join(dataset_path, letter)
            if not os.path.isdir(letter_dir):
                continue
            label = letter.upper()
            if label not in self.reverse_labels:
                continue
            label_id = self.reverse_labels[label]
            count = 0
            for fname in os.listdir(letter_dir):
                if not fname.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
                    continue
                fpath = os.path.join(letter_dir, fname)
                try:
                    img = Image.open(fpath).convert('RGB')
                    feats = extract_hog_features(img)
                    X.append(feats)
                    y.append(label_id)
                    count += 1
                except Exception as e:
                    print(f"  Skip {fname}: {e}")
            print(f"  {label}: {count} images loaded")

        if len(X) < 10:
            print("Not enough training data!")
            return False

        X = np.array(X)
        y = np.array(y)
        print(f"Training on {len(X)} samples, {len(set(y))} classes")

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        self.model = SVC(
            kernel='rbf',
            C=10,
            gamma='scale',
            probability=True,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        self.save_model()
        print("Model trained and saved.")
        return True

    def train(self, training_data, training_labels):
        """Train using pre-loaded images (numpy arrays)."""
        try:
            X, y = [], []
            for image, label in zip(training_data, training_labels):
                feats = extract_hog_features(image)
                X.append(feats)
                label_id = self.reverse_labels.get(label.upper(), 0) if isinstance(label, str) else int(label)
                y.append(label_id)

            if len(X) < 2:
                return False

            X = np.array(X)
            y = np.array(y)

            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)

            self.model = SVC(
                kernel='rbf',
                C=10,
                gamma='scale',
                probability=True,
                random_state=42
            )
            self.model.fit(X_scaled, y)
            self.save_model()
            return True
        except Exception as e:
            print(f"Training error: {e}")
            return False

    def predict(self, image):
        """Predict gesture from image (numpy array or PIL Image)."""
        try:
            if self.model is None or self.scaler is None:
                return {'error': 'Model not trained', 'gesture': None, 'confidence': 0}

            features = self.extract_hand_features(image)
            if features is None:
                return {'error': 'Feature extraction failed', 'gesture': None, 'confidence': 0}

            features_scaled = self.scaler.transform(features)
            prediction = int(self.model.predict(features_scaled)[0])
            proba = self.model.predict_proba(features_scaled)[0]
            confidence = float(max(proba))

            gesture_name = self.gesture_labels.get(prediction, 'Unknown')

            return {
                'gesture': gesture_name,
                'gesture_id': prediction,
                'confidence': confidence,
                'accuracy': confidence * 100
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            return {'error': str(e), 'gesture': None, 'confidence': 0}

    def save_model(self):
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            print(f"Saved: {self.model_path}, {self.scaler_path}")
        except Exception as e:
            print(f"Save error: {e}")

    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print(f"Model loaded: {self.model_path}")
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
                print(f"Scaler loaded: {self.scaler_path}")
        except Exception as e:
            print(f"Load error: {e}")
            self.model = None
            self.scaler = None

    def add_gesture_label(self, gesture_name):
        if gesture_name not in self.reverse_labels:
            new_id = len(self.gesture_labels)
            self.gesture_labels[new_id] = gesture_name
            self.reverse_labels[gesture_name] = new_id
            return new_id
        return self.reverse_labels[gesture_name]
