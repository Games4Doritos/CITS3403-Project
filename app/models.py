from app import db

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # for clearer output when inspect
    def __repr__(self):
        return f"<Player {self.email}>"