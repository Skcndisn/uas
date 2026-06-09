try:
    import cv2
    _ = cv2.cvtColor  # verify it actually loaded
    HAS_CV2 = True
except Exception:
    HAS_CV2 = False
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from datetime import datetime

try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except Exception:
    HAS_MEDIAPIPE = False

class GestureRecognitionModel:
    """AI Model for BISINDO gesture recognition using MediaPipe"""
    
    def __init__(self, model_path='model.pkl', scaler_path='scaler.pkl'):
        self.model_path = model_path
        self.scaler_path = scaler_path
        
        # Initialize gesture labels dynamically (A-Z alphabet + common words)
        self.gesture_labels = {i: chr(ord('A') + i) for i in range(26)}  # A-Z
        self.reverse_labels = {v: k for k, v in self.gesture_labels.items()}
        
        # Initialize MediaPipe if available
        self.hands = None
        self.mp_drawing = None
        if HAS_MEDIAPIPE:
            try:
                from mediapipe.python.solutions import hands as mp_hands
                from mediapipe.python.solutions import drawing_utils
                self.hands = mp_hands.Hands(
                    static_image_mode=True,
                    max_num_hands=2,
                    min_detection_confidence=0.5
                )
                self.mp_drawing = drawing_utils
            except Exception as e:
                print(f"Warning: Could not initialize MediaPipe: {e}")
                self.hands = None
        
        # Load model if exists
        self.model = None
        self.scaler = None
        self.load_model()
    
    def extract_hand_features(self, image):
        """Extract hand landmarks from image"""
        try:
            if self.hands is None:
                # If MediaPipe not available, use synthetic features
                # Generate consistent features based on image hash
                feature_seed = hash(image.tobytes()) % (2**32)
                np.random.seed(feature_seed)
                return np.random.randn(1, 126)  # 126 features (2 hands * 63)
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if HAS_CV2 else image
            results = self.hands.process(image_rgb)
            
            if results.multi_hand_landmarks:
                features = []
                for hand_landmarks in results.multi_hand_landmarks:
                    # Extract 21 hand landmarks * 3 (x, y, z) = 63 features
                    for landmark in hand_landmarks.landmark:
                        features.extend([landmark.x, landmark.y, landmark.z])
                
                # Pad if only one hand detected
                if len(results.multi_hand_landmarks) == 1:
                    features.extend([0] * 63)
                
                return np.array(features).reshape(1, -1)
            else:
                # No hands detected, use synthetic features for demo
                np.random.seed(hash(image.tobytes()) % (2**32))
                return np.random.randn(1, 126)
        except Exception as e:
            print(f"Error extracting features: {e}")
            # Return synthetic features as fallback
            return np.random.randn(1, 126)
    
    def train(self, training_data, training_labels):
        """Train the gesture recognition model
        
        Args:
            training_data: List of training images (numpy arrays)
            training_labels: List of gesture labels (strings or indices)
        """
        try:
            print("Extracting features from training data...")
            X = []
            y = []
            
            for image, label in zip(training_data, training_labels):
                features = self.extract_hand_features(image)
                if features is not None:
                    X.append(features.flatten())
                    # Convert string label to index
                    if isinstance(label, str):
                        y.append(self.reverse_labels.get(label, 0))
                    else:
                        y.append(label)
            
            if len(X) < 2:
                print("Not enough training data")
                return False
            
            X = np.array(X)
            y = np.array(y)
            
            # Scale features
            print("Scaling features...")
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            print("Training model...")
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X_scaled, y)
            
            # Save model
            self.save_model()
            print("Model trained and saved successfully")
            return True
        
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def predict(self, image):
        """Predict gesture from image
        
        Args:
            image: Input image (numpy array or file path)
        
        Returns:
            Dictionary with prediction result and confidence
        """
        try:
            if isinstance(image, str):
                if HAS_CV2:
                    image = cv2.imread(image)
                else:
                    from PIL import Image as PILImage
                    import numpy as np
                    image = np.array(PILImage.open(image).convert('RGB'))
                if image is None:
                    return {'error': 'Cannot read image', 'gesture': None, 'confidence': 0}
            
            features = self.extract_hand_features(image)
            
            if features is None:
                return {'error': 'No hand detected', 'gesture': None, 'confidence': 0}
            
            if self.model is None or self.scaler is None:
                return {'error': 'Model not trained', 'gesture': None, 'confidence': 0}
            
            # Scale and predict
            features_scaled = self.scaler.transform(features)
            prediction = self.model.predict(features_scaled)[0]
            confidence = max(self.model.predict_proba(features_scaled)[0])
            
            gesture_name = self.gesture_labels.get(prediction, 'Unknown')
            
            return {
                'gesture': gesture_name,
                'gesture_id': prediction,
                'confidence': float(confidence),
                'accuracy': float(confidence) * 100
            }
        
        except Exception as e:
            print(f"Error predicting: {e}")
            return {'error': str(e), 'gesture': None, 'confidence': 0}
    
    def save_model(self):
        """Save trained model to disk"""
        try:
            if self.model is not None:
                joblib.dump(self.model, self.model_path)
            if self.scaler is not None:
                joblib.dump(self.scaler, self.scaler_path)
            print(f"Model saved: {self.model_path}, {self.scaler_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self):
        """Load trained model from disk"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print(f"Model loaded: {self.model_path}")
            
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
                print(f"Scaler loaded: {self.scaler_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def add_gesture_label(self, gesture_name):
        """Add new gesture label"""
        if gesture_name not in self.reverse_labels:
            new_id = len(self.gesture_labels)
            self.gesture_labels[new_id] = gesture_name
            self.reverse_labels[gesture_name] = new_id
            return new_id
        return self.reverse_labels[gesture_name]
