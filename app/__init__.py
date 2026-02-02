from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_mail import Mail
import os
import sys

# Initialize extensions globally
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

# Create global app and ensure ADMINS config is set
def _get_template_folder():
    """Get the correct template folder for both dev and bundled executables"""
    # Check if running as bundled executable
    if getattr(sys, 'frozen', False):
        # When bundled with --add-data "app/templates:app/templates"
        # the templates are at sys._MEIPASS/app/templates
        base_dir = sys._MEIPASS
        template_path = os.path.join(base_dir, 'app', 'templates')
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_dir, 'templates')
    return template_path

def _get_static_folder():
    """Get the correct static folder for both dev and bundled executables"""
    # Check if running as bundled executable
    if getattr(sys, 'frozen', False):
        # When bundled with --add-data "app/static:app/static"
        # the static files are at sys._MEIPASS/app/static
        base_dir = sys._MEIPASS
        static_path = os.path.join(base_dir, 'app', 'static')
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        static_path = os.path.join(base_dir, 'static')
    return static_path

app = Flask(__name__, template_folder=_get_template_folder(), static_folder=_get_static_folder())
app.config.from_object(Config)
if 'ADMINS' not in app.config:
    app.config['ADMINS'] = [app.config.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')]
mail = Mail(app)

def create_app():
    app = Flask(__name__, template_folder=_get_template_folder(), static_folder=_get_static_folder())
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