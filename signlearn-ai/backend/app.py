from flask import Flask
from flask_cors import CORS
from config import DevelopmentConfig
from database.models import db
import os

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
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
