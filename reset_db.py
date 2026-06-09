import os
import sys

# Add path
backend_path = os.path.join(os.getcwd(), 'signlearn-ai', 'backend')
sys.path.insert(0, backend_path)

# Delete database file first (before changing dir)
db_path = os.path.join(os.getcwd(), 'signlearn.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✓ Deleted {db_path}")

# Change to backend directory
os.chdir(backend_path)

# Reinitialize
from config import DevelopmentConfig
from database.models import db
from app import create_app

app = create_app(DevelopmentConfig)
with app.app_context():
    print("✓ Database reinitialized with correct image paths")
    from database.models import Gesture
    gestures = Gesture.query.limit(26).all()
    print(f"\nAll {len(gestures)} gestures:")
    for g in gestures:
        print(f"  {g.name}: {g.image}")
