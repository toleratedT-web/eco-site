import os
from flask import Flask
from config import Config
from extensions import db, login_manager, migrate

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True,
                static_folder="static", template_folder="templates")
    app.config.from_object(config_class)

    # Ensure instance folder exists (for SQLite file)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"              # redirect target for @login_required
    login_manager.login_message_category = "warning"

    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    from .auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app
