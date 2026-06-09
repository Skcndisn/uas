from flask import Flask, send_from_directory, request, Response
from flask_cors import CORS
from config import DevelopmentConfig
from database.models import db
import os

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Create app context for database initialization
    with app.app_context():
        db.create_all()
        
        # Initialize sample gestures if database is empty
        from database.models import Gesture
        if Gesture.query.count() == 0:
            init_sample_gestures()
    
    # Register blueprints
    from routes.gestures import gestures_bp
    from routes.practice import practice_bp
    
    app.register_blueprint(gestures_bp, url_prefix='/api/gestures')
    app.register_blueprint(practice_bp, url_prefix='/api/practice')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'service': 'signlearn-backend'}, 200
    
    # Proxy AI service requests
    import requests as _http_requests
    
    @app.route('/ai/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def ai_proxy(path):
        ai_url = f'http://localhost:5001/{path}'
        try:
            if request.method == 'POST':
                if request.files:
                    files = {k: (v.filename, v.stream, v.content_type) for k, v in request.files.items()}
                    resp = _http_requests.post(ai_url, files=files, data=request.form, timeout=30)
                else:
                    resp = _http_requests.post(ai_url, json=request.get_json(), timeout=30)
            elif request.method == 'GET':
                resp = _http_requests.get(ai_url, params=request.args, timeout=30)
            else:
                resp = _http_requests.request(request.method, ai_url, timeout=30)
            return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))
        except Exception as e:
            return {'success': False, 'error': f'AI service unavailable: {str(e)}'}, 503
    
    # Serve frontend static files
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path and os.path.exists(os.path.join(FRONTEND_DIR, path)):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, 'index.html')
    
    return app

def init_sample_gestures():
    """Initialize BISINDO alphabet gestures"""
    from database.models import Gesture
    
    alphabet = [chr(i) for i in range(ord('A'), ord('Z')+1)]
    
    sample_gestures = []
    for letter in alphabet:
        gesture = Gesture(
            name=f'Huruf {letter}',
            image=f'{letter.lower()}.jpg',
            description=f'Gerakan tangan untuk menyatakan huruf {letter} dalam Bahasa Isyarat Indonesia (BISINDO)'
        )
        sample_gestures.append(gesture)
    
    for gesture in sample_gestures:
        db.session.add(gesture)
    
    db.session.commit()
    print(f"✓ Initialized {len(sample_gestures)} BISINDO alphabet gestures")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
