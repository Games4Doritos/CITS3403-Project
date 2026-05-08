from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class Account(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # one-to-one relationship with Profile
    profile = db.relationship('Profile', backref='account', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # for clearer output when inspect
    def __repr__(self):
        return f"<Account {self.email}>"
    
@login.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))

# Starting the Profile model minimal way for the use of authentication
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(
        db.Integer, 
        db.ForeignKey('account.id'),
        nullable=False
    )
    username = db.Column(
        db.String(50),
        nullable=False
    )

    # Relationship to game sessions
    game_sessions = db.relationship('GameSession', backref='profile', lazy=True)

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Float, nullable=False)  # Duration in milliseconds
    jump_count = db.Column(db.Integer, default=0)   # Total jumps in session
    currency_earned = db.Column(db.Integer, default=0)  # Coins earned
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<GameSession {self.id}: Profile {self.player_id} - Score {self.score}>"