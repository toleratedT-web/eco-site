from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, InputRequired
from wtforms.fields import DateField, TimeField, TextAreaField
from wtforms.validators import Length, DataRequired
import sqlalchemy as sa
from app import db
from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField
from wtforms.validators import  NumberRange
from flask_wtf.file import FileAllowed


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

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

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField(
        'Category',
        choices=[('solar', 'Solar'), ('ev', 'EV'), ('appliances', 'Appliances')],
        validators=[DataRequired()]
    )
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    submit = SubmitField('Save')


class SettingsForm(FlaskForm):
    name = StringField('Full Name', validators=[Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Settings')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')


class SupportForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Send')


class BookingRescheduleForm(FlaskForm):
    date = DateField('New Date', validators=[DataRequired()], format='%Y-%m-%d')
    time = TimeField('New Time', validators=[DataRequired()])
    submit = SubmitField('Reschedule')


class EnergyEntryForm(FlaskForm):
    entry_date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    kwh = FloatField('kWh', validators=[DataRequired()])
    submit = SubmitField('Add Entry')


class EnergyGoalForm(FlaskForm):
    daily_kwh_goal = FloatField('Daily kWh Goal', validators=[DataRequired()])
    submit = SubmitField('Save Goal')