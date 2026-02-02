from app import create_app, db  # Import the factory function that creates the app
from app.models import User
import sys
import os
import webbrowser
import threading




# Use the create_app function to initialize the app with the correct configuration
app = create_app()  # Create the Flask app instance

if __name__ == "__main__":
    with app.app_context():  # Ensure the database is initialized within the app context
        # For first local run on SQLite; afterwards use Flask-Migrate
        db.create_all()  # Create all database tables
    
    # Open browser after a short delay
    def open_browser():
        webbrowser.open('http://127.0.0.1:5000')
    
    threading.Timer(1.5, open_browser).start()
    app.run(debug=False, use_reloader=False)  # Run the app
