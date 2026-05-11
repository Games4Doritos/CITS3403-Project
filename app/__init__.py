from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create extension objects
db = SQLAlchemy()
login = LoginManager()

# Redirect unauthenticated unsers to auth page
login.login_view = 'auth'


def create_app(config):
    # Create Flask app instance with config settings
    app = Flask(__name__)
    app.config.from_object(config)

    # Attach extensions to this app instance
    db.init_app(app)
    login.init_app(app)

    from app import routes
    from app import models

    return app
