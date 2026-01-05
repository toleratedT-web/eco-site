from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

# Initialize extensions globally (do not bind to app yet)
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()

# Optional: create a global app for quick access (e.g., shell)
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions on the global app if you want it usable immediately
db.init_app(app)
migrate.init_app(app, db)
login.init_app(app)
mail.init_app(app)

login.login_view = 'main.login_route'

# Register blueprints for global app (optional, e.g., quick dev testing)
from app.routes import bp as main_bp
app.register_blueprint(main_bp)


# =========================
# App factory
# =========================
def create_app():
    """Factory to create a new Flask app instance (recommended for production/testing)."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions on this app instance
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    login.login_view = 'main.login_route'

    # Register blueprint routes
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app