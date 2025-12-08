from flask import Flask
from config import Config
from app.routes import bp  # Ensure you're importing bp correctly from app.routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configurations from config.py

    app.register_blueprint(bp)  # Register the blueprint so the routes are available

    return app