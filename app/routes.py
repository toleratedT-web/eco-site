from flask import render_template, Flask, request, session, redirect, url_for
from forms import FootprintForm
from flask_login import login_required, current_user

app = Flask(__name__)

@app.route('/')
def home():
    # Your existing home page
    return render_template("home.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


@app.route('/calculate')
def calculate():
    form = FootprintForm()
    if request.method == "POST":
        if form.validate_on_submit():
            # Using average emission factors for calculations
            car_emission_calculation = round(form.car_emission.data * 0.21, 2)
            electricity_calculation = round(form.electricity_usage.data * 0.222, 2)
            total = car_emission_calculation + electricity_calculation
            session['car_emission'] = form.car_emission.data
            session['electricity_usage'] = form.electricity_usage.data
            session['total'] = total
            return redirect(url_for('calculate'))
        
    submitted_car_emission = session.pop('car_emission', None)
    submitted_electricity_usage = session.pop('electricity_usage', None)
    submitted_total = session.pop('total', None)

    return render_template('carbon_calculator.html', title = 'Carbon Footprint Calculator', form = form, submitted_car_emission = submitted_car_emission, submitted_electricity_usage = submitted_electricity_usage, submitted_total = submitted_total)