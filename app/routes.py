from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from urllib.parse import urlsplit
from app import db, login
from app.forms import LoginForm, RegistrationForm, FootprintForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app.models import User

# Blueprint for routes
bp = Blueprint('main', __name__)

# Load user for Flask-Login
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/green_products')
def green_products():
    return render_template('green_products.html')

@bp.route('/consultation')
def consultation():
    return render_template('consultation.html')

@bp.route('/energy_tracker')
def energy_tracker():
    return render_template('energy_tracker.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


@bp.route('/login', methods=['GET', 'POST'])
def login_route():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login_route'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout_route():
    logout_user()
    return redirect(url_for('main.home'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login_route'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    return render_template('reset_password.html', title='Reset Password')


@bp.route('/calculate', methods=['GET', 'POST'])
def calculate():
    form = FootprintForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            car_emission_calculation = round(form.car_emission.data * 0.21, 2)
            electricity_calculation = round(form.electricity_usage.data * 0.222, 2)
            total = car_emission_calculation + electricity_calculation
            session['car_emission'] = form.car_emission.data
            session['electricity_usage'] = form.electricity_usage.data
            session['total'] = total
            return redirect(url_for('main.calculate'))

    submitted_car_emission = session.pop('car_emission', None)
    submitted_electricity_usage = session.pop('electricity_usage', None)
    submitted_total = session.pop('total', None)

    return render_template('carbon_calculator.html', title='Carbon Footprint Calculator', form=form,
                           submitted_car_emission=submitted_car_emission,
                           submitted_electricity_usage=submitted_electricity_usage,
                           submitted_total=submitted_total)