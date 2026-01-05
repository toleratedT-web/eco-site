from flask_mail import Message
from app import mail
from flask import render_template
from app import app
from itsdangerous import URLSafeTimedSerializer

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def veriy_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=expiration
        )
    except:
        return None
    return email

from flask_mail import Message
from flask import url_for

def send_password_reset_email(user_email):
    token = generate_reset_token(user_email)
    reset_url = url_for(
        "reset_password",
        token=token,
        _external=True
    )

    msg = Message(
        subject="Password Recovery",
        recipients=[user_email],
        body=f"""To reset your password, click the link below:

{reset_url}

If you did not request this, ignore this email.
"""
    )

    mail.send(msg)