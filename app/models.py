from app import db
from datetime import datetime

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # Relationship to game sessions
    game_sessions = db.relationship('GameSession', backref='player', lazy=True)
    
    def __repr__(self):
        return f"<Player {self.email}>"

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, default=0)  # Duration in seconds
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<GameSession {self.id}: Player {self.player_id} - Score {self.score}>"