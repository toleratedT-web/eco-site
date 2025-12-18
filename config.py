import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallbacksecretkey')

    # Ensure the database is SQLite
    INSTANCE_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    if not os.path.exists(INSTANCE_FOLDER):
        os.makedirs(INSTANCE_FOLDER)

    # SQLite URI
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_FOLDER, 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    # Email sender for password reset
    ADMINS = [os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')]