from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, InputRequired
from wtforms.fields import DateField, TimeField, TextAreaField
from wtforms.validators import Length
import sqlalchemy as sa
from app import db
from app.models import User

class FootprintForm(FlaskForm):
    car_emission = FloatField("Car Emission", validators=[InputRequired()])  # Corrected here
    electricity_usage = FloatField("Electricity Usage", validators=[InputRequired()])  # Corrected here
    submit = SubmitField("Submit")

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class BookingForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    date = DateField('Preferred Date', validators=[DataRequired()], format='%Y-%m-%d')
    time = TimeField('Preferred Time', validators=[DataRequired()])
    notes = TextAreaField('Notes (optional)', validators=[Length(max=1000)])
    submit = SubmitField('Request Booking')