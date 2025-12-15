<<<<<<< HEAD
=======
from app import create_app, db  # Import the factory function that creates the app
from app.models import User
>>>>>>> fddfc1aa847306ac5fbb88a3306270d248ef156e
import sys
import os
from app import create_app
from extensions import db


# Use the create_app function to initialize the app with the correct configuration
app = create_app()  # Create the Flask app instance

if __name__ == "__main__":
    with app.app_context():  # Ensure the database is initialized within the app context
        # For first local run on SQLite; afterwards use Flask-Migrate
        db.create_all()  # Create all database tables
    app.run(debug=True)  # Run the app
>>>>>>> fddfc1aa847306ac5fbb88a3306270d248ef156e
