from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
try:
    import cv2
    HAS_CV2 = True
except Exception:
    HAS_CV2 = False
import numpy as np
from io import BytesIO
from PIL import Image
from model import GestureRecognitionModel
import os

app = Flask(__name__)
CORS(app)

# Initialize model
model = GestureRecognitionModel()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'signlearn-ai-service',
        'model_loaded': model.model is not None
    }), 200

@app.route('/predict', methods=['POST'])
def predict():
    """Predict gesture from uploaded image"""
    try:
        # Check if model is trained
        if model.model is None:
            return jsonify({
                'success': False,
                'error': 'Model not trained. Please train the model first.',
                'gesture': None,
                'confidence': 0
            }), 503
        
        # Get image from request
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image provided',
                'gesture': None,
                'confidence': 0
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'gesture': None,
                'confidence': 0
            }), 400
        
        # Read image
        image_data = file.read()
        image = Image.open(BytesIO(image_data)).convert('RGB')
        image = np.array(image)
        if HAS_CV2:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Make prediction
        result = model.predict(image)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error'],
                'gesture': result.get('gesture'),
                'confidence': result.get('confidence', 0)
            }), 400
        
        return jsonify({
            'success': True,
            'gesture': result['gesture'],
            'gesture_id': result.get('gesture_id'),
            'confidence': result['confidence'],
            'accuracy': result['accuracy']
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}',
            'gesture': None,
            'confidence': 0
        }), 500

@app.route('/train', methods=['POST'])
def train_model():
    """Train model with uploaded images"""
    try:
        if 'images' not in request.files or 'labels' not in request.form:
            return jsonify({
                'success': False,
                'error': 'Images and labels required'
            }), 400
        
        files = request.files.getlist('images')
        labels = request.form.get('labels', '').split(',')
        
        if len(files) != len(labels):
            return jsonify({
                'success': False,
                'error': 'Number of images and labels must match'
            }), 400
        
        # Load images
        training_data = []
        training_labels = []
        
        for file, label in zip(files, labels):
            try:
                image_data = file.read()
                image = Image.open(BytesIO(image_data)).convert('RGB')
                image = np.array(image)
                if HAS_CV2:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                training_data.append(image)
                training_labels.append(label.strip())
            except Exception as e:
                print(f"Error processing image: {e}")
        
        if len(training_data) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 training samples required'
            }), 400
        
        # Train model
        success = model.train(training_data, training_labels)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Model trained successfully',
                'samples': len(training_data)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Model training failed'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Training error: {str(e)}'
        }), 500

@app.route('/labels', methods=['GET'])
def get_labels():
    """Get all gesture labels"""
    return jsonify({
        'success': True,
        'labels': model.gesture_labels,
        'reverse_labels': model.reverse_labels
    }), 200

@app.route('/add-label', methods=['POST'])
def add_label():
    """Add new gesture label"""
    try:
        data = request.get_json()
        gesture_name = data.get('gesture_name')
        
        if not gesture_name:
            return jsonify({
                'success': False,
                'error': 'Gesture name required'
            }), 400
        
        gesture_id = model.add_gesture_label(gesture_name)
        
        return jsonify({
            'success': True,
            'gesture_name': gesture_name,
            'gesture_id': gesture_id
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
