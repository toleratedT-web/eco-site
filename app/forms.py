from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from wtforms.validators import InputRequired

class FootprintForm(FlaskForm):
    car_emission = FloatField("Car Emission", validators=[InputRequired])
    electricity_usage = FloatField("Electricity Usage", validators=[InputRequired])
    submit = SubmitField("Submit")
