from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='user') # 'admin' or 'user'
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_path = db.Column(db.String(200))
    detected_food = db.Column(db.String(100))
    protein = db.Column(db.Float)
    fiber = db.Column(db.Float)
    fat = db.Column(db.Float)
    carbs = db.Column(db.Float)
    health_score = db.Column(db.Integer)
    ai_suggestions = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class SymptomLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    symptom_score = db.Column(db.Integer) # 0-5 scale
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)