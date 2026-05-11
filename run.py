from app import create_app, db
from app.config import DeploymentConfig
from flask_migrate import Migrate

app = create_app(DeploymentConfig)

# Attach Flask-Migrate to deployment app
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)