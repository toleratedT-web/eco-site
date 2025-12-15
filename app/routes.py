from flask import render_template, flash, redirect, url_for, request, session
from urllib.parse import urlsplit
from app import db, login
from app.forms import LoginForm, RegistrationForm, FootprintForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app.models import User

# Load user for Flask-Login
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

def init_routes(app):  # Define a function to register the routes
    @app.route('/')
    def home():
        return render_template("home.html")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html", user=current_user)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))  # Redirect to home if already logged in
        form = LoginForm()
        if form.validate_on_submit():
            user = db.session.scalar(
                sa.select(User).where(User.username == form.username.data))
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('home')  # Redirect to home after successful login
            return redirect(next_page)
        return render_template('login.html', title='Sign In', form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('home'))  # Redirect to home after logout

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))  # Redirect to home if already registered/logged in
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)

    @app.route('/calculate', methods=["GET", "POST"])
    def calculate():
        form = FootprintForm()
        if request.method == "POST":
            if form.validate_on_submit():
                car_emission_calculation = round(form.car_emission.data * 0.21, 2)
                electricity_calculation = round(form.electricity_usage.data * 0.222, 2)
                total = car_emission_calculation + electricity_calculation
                session['car_emission'] = form.car_emission.data
                session['electricity_usage'] = form.electricity_usage.data
                session['total'] = total
                return redirect(url_for('calculate'))  # Redirect after form submission

        # Pop the session values to display them
        submitted_car_emission = session.pop('car_emission', None)
        submitted_electricity_usage = session.pop('electricity_usage', None)
        submitted_total = session.pop('total', None)

        return render_template('carbon_calculator.html', title='Carbon Footprint Calculator', form=form, 
                               submitted_car_emission=submitted_car_emission, 
                               submitted_electricity_usage=submitted_electricity_usage, 
                               submitted_total=submitted_total)