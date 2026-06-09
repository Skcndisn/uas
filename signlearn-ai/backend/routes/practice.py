from flask import Blueprint, jsonify, request
from database.models import db, PracticeResult, Gesture
import uuid
import requests
from flask import current_app

practice_bp = Blueprint('practice', __name__)

@practice_bp.route('/gestures', methods=['GET'])
def get_practice_gestures():
    """Get random gestures for practice"""
    try:
        count = request.args.get('count', 5, type=int)
        gestures = Gesture.query.order_by(db.func.random()).limit(count).all()
        
        return jsonify({
            'success': True,
            'data': [gesture.to_dict() for gesture in gestures]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@practice_bp.route('/submit', methods=['POST'])
def submit_practice():
    """Submit practice result"""
    try:
        data = request.get_json()
        
        if not data or not data.get('gesture_id') or data.get('accuracy') is None:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        gesture = Gesture.query.get(data['gesture_id'])
        if not gesture:
            return jsonify({'success': False, 'error': 'Gesture not found'}), 404
        
        # Generate or get user ID
        user_id = data.get('user_id', str(uuid.uuid4()))
        
        # Determine status based on accuracy
        accuracy = float(data['accuracy'])
        if accuracy >= 0.8:
            status = 'correct'
        elif accuracy >= 0.5:
            status = 'partial'
        else:
            status = 'incorrect'
        
        practice_result = PracticeResult(
            user_id=user_id,
            gesture_id=data['gesture_id'],
            accuracy=accuracy,
            status=status
        )
        
        db.session.add(practice_result)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': practice_result.to_dict(),
            'user_id': user_id,
            'message': f'Practice result saved with status: {status}'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@practice_bp.route('/results/<user_id>', methods=['GET'])
def get_user_results(user_id):
    """Get practice results for a user"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = PracticeResult.query.filter_by(user_id=user_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        results = [result.to_dict() for result in query.items]
        
        # Add gesture info to each result
        for result in results:
            gesture = Gesture.query.get(result['gesture_id'])
            if gesture:
                result['gesture'] = gesture.to_dict()
        
        return jsonify({
            'success': True,
            'data': results,
            'pagination': {
                'total': query.total,
                'pages': query.pages,
                'current_page': page,
                'per_page': per_page
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@practice_bp.route('/stats/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """Get practice statistics for a user"""
    try:
        all_results = PracticeResult.query.filter_by(user_id=user_id).all()
        
        if not all_results:
            return jsonify({
                'success': True,
                'data': {
                    'total_practices': 0,
                    'correct': 0,
                    'partial': 0,
                    'incorrect': 0,
                    'average_accuracy': 0,
                    'accuracy_by_gesture': {}
                }
            }), 200
        
        stats = {
            'total_practices': len(all_results),
            'correct': len([r for r in all_results if r.status == 'correct']),
            'partial': len([r for r in all_results if r.status == 'partial']),
            'incorrect': len([r for r in all_results if r.status == 'incorrect']),
            'average_accuracy': sum(r.accuracy for r in all_results) / len(all_results),
            'accuracy_by_gesture': {}
        }
        
        # Calculate accuracy per gesture
        gesture_results = {}
        for result in all_results:
            if result.gesture_id not in gesture_results:
                gesture_results[result.gesture_id] = []
            gesture_results[result.gesture_id].append(result.accuracy)
        
        for gesture_id, accuracies in gesture_results.items():
            gesture = Gesture.query.get(gesture_id)
            if gesture:
                stats['accuracy_by_gesture'][gesture.name] = {
                    'count': len(accuracies),
                    'average': sum(accuracies) / len(accuracies),
                    'best': max(accuracies),
                    'worst': min(accuracies)
                }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@practice_bp.route('/predict', methods=['POST'])
def predict_gesture():
    """Call AI service to predict gesture from image"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        file = request.files['image']
        
        # Forward to AI service
        ai_service_url = 'http://localhost:5001/predict'
        
        try:
            response = requests.post(
                ai_service_url,
                files={'image': file.stream},
                timeout=10
            )
            
            if response.status_code == 200:
                prediction = response.json()
                return jsonify({
                    'success': True,
                    'data': prediction
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'AI service error'
                }), 500
        except requests.exceptions.RequestException as e:
            return jsonify({
                'success': False,
                'error': f'Cannot connect to AI service: {str(e)}'
            }), 503
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
