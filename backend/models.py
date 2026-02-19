from datetime import datetime
import hashlib

# Simple MVP Models without ORM complexity if possible, but ORM easier for quick dev
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.phone}>'

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    hash_signature = db.Column(db.String(64))  # Simple hash for integrity

    def calculate_hash(self):
        # Basic hash of critical fields
        data = f"{self.user_id}{self.amount}{self.date.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    skills_required = db.Column(db.String(255)) # Comma separated
    min_salary = db.Column(db.Integer)
    max_salary = db.Column(db.Integer)

