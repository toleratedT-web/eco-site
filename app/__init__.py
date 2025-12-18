from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_mail import Mail

# Initialize extensions globally
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    login.login_view = 'main.login_route'  # Define the login route for Flask-Login

    # Register blueprint routes after initializing the app
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app