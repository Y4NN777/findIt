from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialisation de SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    """Représente un utilisateur dans la base de données."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    
    # Relations
    lost_items = db.relationship('LostItem', backref='user', lazy=True)
    found_items = db.relationship('FoundItem', backref='user', lazy=True)

class LostItem(db.Model):
    """Représente un objet perdu."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    date_lost = db.Column(db.Date, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    contact_method = db.Column(db.String(20), nullable=False, default='email')
    contact_info = db.Column(db.String(200), nullable=True)
    reward = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, resolved, expired
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class FoundItem(db.Model):
    """Représente un objet retrouvé."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    date_found = db.Column(db.Date, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    contact_method = db.Column(db.String(20), nullable=False, default='email')
    contact_info = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, resolved, expired
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class ResolvedMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lost_item_id = db.Column(db.Integer, db.ForeignKey('lost_item.id'), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey('found_item.id'), nullable=False)
    resolved_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resolution_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    lost_item = db.relationship('LostItem', backref='resolved_matches')
    found_item = db.relationship('FoundItem', backref='resolved_matches')
    resolved_by = db.relationship('User', backref='resolved_matches')
