from flask import Blueprint, jsonify, render_template, flash, redirect, url_for, request, session, abort
from urllib.parse import urlsplit
from app import db, login
from app.forms import LoginForm, RegistrationForm, FootprintForm, BookingForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from sqlalchemy import func
from app.models import User, Booking, Product, Footprint
import datetime

# Blueprint for routes
bp = Blueprint('main', __name__)

# Load user for Flask-Login
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/green-products')
def green_products():
    solar_products = Product.query.filter_by(category="solar").all()
    ev_products = Product.query.filter_by(category="ev").all()
    appliance_products = Product.query.filter_by(category="appliances").all()
    return render_template(
        'green_products.html', 
        solar_products=solar_products, 
        ev_products=ev_products,
        appliance_products=appliance_products
    )

@bp.route('/consultation', methods=['GET', 'POST'])
def consultation():
    form = BookingForm()
    if form.validate_on_submit():
        appointment_dt = datetime.datetime.combine(form.date.data, form.time.data)
        booking = Booking(
            user_id=current_user.id if current_user.is_authenticated else None,
            name=form.name.data,
            email=form.email.data,
            appointment_datetime=appointment_dt,
            notes=form.notes.data,
        )
        db.session.add(booking)
        db.session.commit()
        flash('Your booking request has been submitted. We will contact you to confirm.')
        return redirect(url_for('main.consultation'))

    bookings = db.session.scalars(sa.select(Booking).order_by(Booking.appointment_datetime.desc())).all()
    return render_template('consultation.html', form=form, bookings=bookings)

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


@bp.route("/footprint_dashboard")
#@login_required
def footprint_dashboard():
    footprints = Footprint.query.order_by(Footprint.car_emission).all()
    return render_template("footprint_dashboard.html", footprints=footprints)

@bp.route('/carbon_calculator', methods=['GET', 'POST'])
#@login_required
def carbon_calculator():
    form = FootprintForm()
    if request.method == "POST":
        if form.validate_on_submit():
            footprint = Footprint(
                name=form.name.data, #current_user.id,
                car_emission=round((form.car_emission.data * 0.21), 2),
                electricity_usage=round((form.electricity_usage.data * 0.222), 2),
                total_footprint=round(((form.car_emission.data * 0.21) + (form.electricity_usage.data * 0.222)), 2)
            )
            db.session.add(footprint)
            db.session.commit()
            return redirect(url_for('main.footprint_dashboard'))

    return render_template('carbon_calculator.html', title='Carbon Footprint Calculator', form=form)

@bp.route("/delete/<id>", methods=["POST"])
def delete(id):
    footprint = Footprint.query.get_or_404(id)
    db.session.delete(footprint)
    db.session.commit()
    return redirect(url_for('main.footprint_dashboard'))

@bp.route("/api/total-footprints")
def total_footprints():
    total = db.session.query(func.sum(Footprint.total_footprint)).scalar() or 0
    return jsonify({"total_footprints": total})

@bp.route("/api/top-five-footprints")
def top_five_footprints():
    results = (
        db.session.query(Footprint.name, func.sum(Footprint.total_footprint))
        .group_by(Footprint.name)
        .order_by(func.sum(Footprint.total_footprint).desc())
        .limit(5)
        .all()
    )

    data = [
        {"name": name, "total": total}
        for name, total in results
    ]
    return jsonify(data)

@bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.is_admin:
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials', 'danger')
    return render_template('admin_login.html', form=form)

@bp.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    total_bookings = Booking.query.count()
    upcoming_bookings = Booking.query.filter(Booking.appointment_datetime >= datetime.utcnow()).count()
    past_bookings = total_bookings - upcoming_bookings
    recent = Booking.query.order_by(Booking.id.desc()).limit(10).all()
    # add any other analytics queries (group by month, source, etc.)
    return render_template('admin_dashboard.html',
                           total=total_bookings,
                           upcoming=upcoming_bookings,
                           past=past_bookings,
                           recent=recent)