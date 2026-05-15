from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import random
import string


class Account(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    friend_code = db.Column(db.String(8), nullable=False)

    # one-to-one relationship with Profile
    profile = db.relationship('Profile', backref='account', uselist=False, cascade='all, delete-orphan')
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
    username = db.Column(db.String(18), nullable=False)

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

class Friendship(db.Model):
    # account id's of the two users in the friendship
    friendID1 = db.Column(db.Integer, db.ForeignKey("account.id"), primary_key=True)
    friendID2 = db.Column(db.Integer, db.ForeignKey("account.id"), primary_key=True)
    pending = db.Column(db.Boolean, default=True, nullable=False)

class Sabotage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Who is being sabotaged
    target_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    # Who sent the sabotage
    sender_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    # Multiplier reduction amount
    multiplier_debuff = db.Column(db.Float, default=0.5)
    # Sabotage lasts for 1 run (deactivated after run ends)
    active = db.Column(db.Boolean, default=True)

    # Relationships
    target = db.relationship('Account', foreign_keys=[target_id], backref='received_sabotages')
    sender = db.relationship('Account', foreign_keys=[sender_id], backref='sent_sabotages')

    def __repr__(self):
        return f"<Sabotage from Account {self.sender_id} to Account {self.target_id}>"