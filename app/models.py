from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import random
import string

class Account(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    friend_code = db.Column(db.String(8), nullable=False)

    # one-to-one relationship with Profile
    profile = db.relationship('Profile',backref='account',uselist=False,cascade='all, delete-orphan'
)
    # one-to-one relationship with BestStats
    best_stats = db.relationship('BestStats', backref='account', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_friend_code(self, length=8):
        if not self.friend_code: 
            possible_element = string.ascii_uppercase + string.digits
            while True:
                code = ''.join(random.choices(possible_element, k=length))
                existing_code = Account.query.filter_by(friend_code=code).first()
                if not existing_code:
                    self.friend_code = code
                    break 

    def __repr__(self):
        return f"<Account {self.email}>"
    
@login.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))

class Profile(db.Model):
    # id links directly to Account.id
    id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)

    username = db.Column(
        db.String(50),
        nullable=False
    )

    def __repr__(self):
        return f"<Profile for Account {self.account.email}>"
    
class BestStats(db.Model):
    # id links to Account.id directly
    id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)
    highscore = db.Column(db.Integer, default=0)
    longest_time = db.Column(db.Float, default=0.0)  # in seconds, rounded to 2 d.p
    jump_count = db.Column(db.Integer, default=0)     # total jump count across all runs
    currency = db.Column(db.Integer, default=0)       # total currency across all runs
    total_games = db.Column(db.Integer, default=0)    # total games played

    def __repr__(self):
        return f"<BestStats for Account {self.id} - Highscore: {self.highscore}>"