import sys
import os
from app import create_app
from extensions import db

# Determine template and static folders if running as an exe
extra_args = {}
if getattr(sys, 'frozen', False):
    extra_args = {
        'template_folder': os.path.join(sys._MEIPASS, 'templates'),
        'static_folder': os.path.join(sys._MEIPASS, 'static')
    }

# Create Flask app via factory
app = create_app(**extra_args)

if __name__ == "__main__":
    with app.app_context():
        # Create tables for first run; afterwards use Flask-Migrate
        db.create_all()

    app.run(debug=True)