from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON

db = SQLAlchemy()

class Gesture(db.Model):
    __tablename__ = 'gestures'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    image = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    practice_results = db.relationship('PracticeResult', backref='gesture', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        # Extract letter from gesture name (e.g., "Huruf A" -> "a")
        import re
        # Match pattern "Huruf X" where X is the letter we want
        name_match = re.search(r'Huruf\s+([A-Z])', self.name)
        letter = name_match.group(1).lower() if name_match else None
        
        # Use API endpoint to serve images
        image_url = ''
        if letter:
            image_url = f'/api/images/{letter}'
        elif self.image:
            # Fallback to stored image path
            image_url = self.image
            if image_url and not image_url.startswith('/'):
                image_url = '/' + image_url
        
        return {
            'id': self.id,
            'name': self.name,
            'image': image_url,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class PracticeResult(db.Model):
    __tablename__ = 'practice_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)  # Anonymous user ID
    gesture_id = db.Column(db.Integer, db.ForeignKey('gestures.id'), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)  # 0-1 or 0-100
    status = db.Column(db.String(20), nullable=False)  # 'correct', 'incorrect', 'partial'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'gesture_id': self.gesture_id,
            'accuracy': self.accuracy,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
