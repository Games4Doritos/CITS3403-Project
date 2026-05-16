# Force Flask CLI to import run.py
# Required so Flask-Migrate is initialized and `flask db` commands work
FLASK_APP=run:app
