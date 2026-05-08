from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

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