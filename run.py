from app  # Import the factory function that creates the app
from app.models import User

import sys
import os
from flask import Flask

app = Flask(__name__)

if getattr(sys, 'frozen', False):  # Running as .exe
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:  # Running normally
    app = Flask(__name__, template_folder='templates', static_folder='static')

app = create_app()  # Create the Flask app instance

if __name__ == "__main__":
    with app.app_context():
        # For first local run on SQLite; afterwards use Flask-Migrate
        db.create_all()
    app.run(debug=True)
