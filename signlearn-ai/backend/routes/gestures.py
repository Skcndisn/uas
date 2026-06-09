from flask import Blueprint, jsonify, request
from database.models import db, Gesture
from werkzeug.utils import secure_filename
from flask import current_app
import os

gestures_bp = Blueprint('gestures', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@gestures_bp.route('', methods=['GET'])
def get_all_gestures():
    """Get all available gestures"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Gesture.query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'success': True,
            'data': [gesture.to_dict() for gesture in query.items],
            'pagination': {
                'total': query.total,
                'pages': query.pages,
                'current_page': page,
                'per_page': per_page
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gestures_bp.route('/<int:gesture_id>', methods=['GET'])
def get_gesture(gesture_id):
    """Get specific gesture by ID"""
    try:
        gesture = Gesture.query.get(gesture_id)
        if not gesture:
            return jsonify({'success': False, 'error': 'Gesture not found'}), 404
        
        return jsonify({
            'success': True,
            'data': gesture.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@gestures_bp.route('', methods=['POST'])
def create_gesture():
    """Create new gesture"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        if Gesture.query.filter_by(name=data['name']).first():
            return jsonify({'success': False, 'error': 'Gesture already exists'}), 409
        
        gesture = Gesture(
            name=data['name'],
            image=data.get('image', 'default.jpg'),
            description=data.get('description', '')
        )
        
        db.session.add(gesture)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': gesture.to_dict(),
            'message': 'Gesture created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@gestures_bp.route('/<int:gesture_id>', methods=['PUT'])
def update_gesture(gesture_id):
    """Update existing gesture"""
    try:
        gesture = Gesture.query.get(gesture_id)
        if not gesture:
            return jsonify({'success': False, 'error': 'Gesture not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            gesture.name = data['name']
        if 'image' in data:
            gesture.image = data['image']
        if 'description' in data:
            gesture.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': gesture.to_dict(),
            'message': 'Gesture updated successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@gestures_bp.route('/<int:gesture_id>', methods=['DELETE'])
def delete_gesture(gesture_id):
    """Delete gesture"""
    try:
        gesture = Gesture.query.get(gesture_id)
        if not gesture:
            return jsonify({'success': False, 'error': 'Gesture not found'}), 404
        
        db.session.delete(gesture)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Gesture deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@gestures_bp.route('/upload', methods=['POST'])
def upload_gesture_image():
    """Upload gesture image"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'path': f'/resources/gestures/{filename}'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
