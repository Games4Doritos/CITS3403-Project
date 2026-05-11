import os

# Get the absolute path of the folder where this config.py file is located
# (To build file path reliably)
basedir = os.path.abspath(os.path.dirname(__file__))
default_db_path = 'sqlite:///' + os.path.join(basedir, 'game.db') # could move to instance/ later if needed

class Config:
    SECRET_KEY = os.environ.get("GAME_SECRET_KEY")

    # disable unnecessary tracking to improve performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False 

    # enable CSRF protection for forms
    WTF_CSRF_ENABLED = True


class DeploymentConfig(Config):
    # Use database URL from environment if needed later
    # otherwise use local SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get('GAME_DATABASE_URL') or default_db_path

    # DEBUG = False 

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///memory'
    TESTING = True

    # Disable CSRF protection during automated tests
    WTF_CSRF_ENABLED = False
