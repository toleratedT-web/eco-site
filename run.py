from app import create_app  # Import the factory function that creates the app
from extensions import db
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

if __name__ == '__main__':  # Ensure the app only runs if this file is executed directly
    app.run(debug=True)  # Run the app in debug mode for easier debugging