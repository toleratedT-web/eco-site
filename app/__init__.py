
# app/__init__.py
import os
from flask import Flask
from config import Config
from extensions import db, login_manager, migrate

def create_app(config_class=Config):
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="static",
        template_folder="templates"
    )
    app.config.from_object(config_class)

    # Ensure instance folder exists for SQLite
    os.makedirs(app.instance_path, exist_ok=True)

    # --- Initialize extensions (order matters, but this is fine) ---
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)               # <-- Must succeed
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    # --- Register blueprints ---
    from .routes import main_bp
    app.register_blueprint(main_bp)

    from .auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # --- Register user loader (lazy import to avoid circular deps) ---
    @login_manager.user_loader
    def load_user(user_id: str):
        from .models import User
        return db.session.get(User, int(user_id))

