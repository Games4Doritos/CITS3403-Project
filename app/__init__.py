from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# Create extension objects
db = SQLAlchemy()
login = LoginManager()
mail = Mail()

# Redirect unauthenticated users to auth page
login.login_view = "auth.auth_page"


def create_app(config):
    # Create Flask app instance with config settings
    app = Flask(__name__)
    app.config.from_object(config)

    # Attach extensions to this app instance
    db.init_app(app)
    login.init_app(app)
    mail.init_app(app)

    # register blueprint
    from app.routes import main, auth, user, game, leaderboard

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(game)
    app.register_blueprint(leaderboard)

    from app import models

    return app
