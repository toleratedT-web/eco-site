from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired

class FootprintForm(FlaskForm):
    car_emission = FloatField("Car Emission", validators=[InputRequired])
    electricity_usage = FloatField("Electricity Usage", validators=[InputRequired])
    submit = SubmitField("Submit")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create account")

class LoginForm(FlaskForm):
    email_or_username = StringField("Email or Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
