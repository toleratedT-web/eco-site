from flask_mail import Message
from flask import url_for, current_app
from itsdangerous import URLSafeTimedSerializer
from app import mail
from app.models import User

def generate_reset_token(user_id):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user_id, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        user_id = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except:
        return None
    return User.query.get(user_id)

def send_password_reset_email(user):
    token = generate_reset_token(user.id)
    reset_url = url_for("main.reset_password", token=token, _external=True)

    msg = Message(
        subject="Password Recovery",
        recipients=[user.email],  # must be email string
        body=f"""To reset your password, click the link below:

{reset_url}

If you did not request this, ignore this email.
"""
    )
    mail.send(msg)