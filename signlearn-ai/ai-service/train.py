import os
import cv2
import numpy as np
from model import GestureRecognitionModel
import argparse
from pathlib import Path

def load_training_data(dataset_path):
    """Load training data from dataset directory
    
    Expected structure for BISINDO Alphabet:
    dataset/
        ├── A/
        │   ├── image1.jpg
        │   ├── image2.jpg
        ├── B/
        ├── ...
        └── Z/
    """
    training_data = []
    training_labels = []
    
    if not os.path.exists(dataset_path):
        print(f"Dataset path does not exist: {dataset_path}")
        return training_data, training_labels
    
    gesture_dirs = sorted([d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))])
    print(f"Found {len(gesture_dirs)} gesture directories: {gesture_dirs}\n")
    
    for gesture_name in gesture_dirs:
        gesture_path = os.path.join(dataset_path, gesture_name)
        
        if not os.path.isdir(gesture_path):
            continue
        
        print(f"Loading gesture: {gesture_name}")
        count = 0
        
        for image_file in os.listdir(gesture_path):
            image_path = os.path.join(gesture_path, image_file)
            
            if not image_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
                continue
            
            try:
                image = cv2.imread(image_path)
                if image is not None:
                    # Resize image to standard size for consistency
                    image = cv2.resize(image, (320, 240))
                    training_data.append(image)
                    training_labels.append(gesture_name)
                    count += 1
            except Exception as e:
                print(f"  Error loading {image_file}: {e}")
        
        print(f"  ✓ Loaded {count} images")
    
    print(f"\n{'='*50}")
    print(f"Total training samples: {len(training_data)}")
    print(f"{'='*50}\n")
    return training_data, training_labels

def create_sample_training_data():
    """Create sample synthetic training data for testing"""
    print("Creating sample training data...")
    
    training_data = []
    training_labels = []
    
    # Generate synthetic data for A-Z alphabet
    alphabet = [chr(i) for i in range(ord('A'), ord('Z')+1)]
    
    # Create synthetic images (blank images for demo)
    for letter in alphabet:
        for i in range(5):  # 5 samples per letter
            # Create a simple image with random content
            image = np.random.randint(100, 200, (240, 320, 3), dtype=np.uint8)
            # Add some structure to make it more realistic
            cv2.circle(image, (160, 120), 40, (0, 255, 0), -1)
            cv2.putText(image, letter, (140, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
            
            training_data.append(image)
            training_labels.append(letter)
    
    print(f"Created {len(training_data)} synthetic training samples\n")
    return training_data, training_labels

def train_model(dataset_path=None, use_sample_data=False):
    """Train gesture recognition model
    
    Args:
        dataset_path: Path to dataset folder (default: ./dataset)
        use_sample_data: Whether to use sample synthetic data
    """
    print("=" * 60)
    print("BISINDO Alphabet Gesture Recognition - Model Training")
    print("=" * 60)
    print()
    
    # Initialize model
    model = GestureRecognitionModel()
    
    # Determine dataset path
    if dataset_path is None:
        dataset_path = os.path.join(os.path.dirname(__file__), 'dataset')
    
    # Load training data
    if os.path.exists(dataset_path) and not use_sample_data:
        print(f"Loading real dataset from: {dataset_path}\n")
        training_data, training_labels = load_training_data(dataset_path)
    elif use_sample_data:
        print("Using synthetic sample data\n")
        training_data, training_labels = create_sample_training_data()
    else:
        print(f"Dataset not found at: {dataset_path}")
        print("Using synthetic sample data instead\n")
        training_data, training_labels = create_sample_training_data()
    
    if len(training_data) == 0:
        print("ERROR: No training data loaded")
        return False
    
    # Train model
    print("Training model...")
    print("-" * 60)
    success = model.train(training_data, training_labels)
    
    if success:
        print("\n" + "=" * 60)
        print("✓ Model training completed successfully!")
        print("=" * 60)
        print(f"Model saved as: {model.model_path}")
        print(f"Scaler saved as: {model.scaler_path}")
        print(f"Total training samples: {len(training_data)}")
        print(f"Unique gestures: {len(set(training_labels))}")
        print("=" * 60)
        return True
    else:
        print("\nERROR: Model training failed")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train BISINDO gesture recognition model')
    parser.add_argument('--dataset', type=str, default='dataset', help='Path to dataset directory (default: ./dataset)')
    parser.add_argument('--sample', action='store_true', help='Use synthetic sample data instead of real dataset')
    
    args = parser.parse_args()
    
    train_model(dataset_path=args.dataset, use_sample_data=args.sample)
