from flask import Blueprint, render_template, flash, redirect, url_for, request, session, abort
from urllib.parse import urlsplit
from app import db, login
from app.forms import LoginForm, RegistrationForm, FootprintForm, BookingForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app.models import User, Booking, Product
import datetime
from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email
from datetime import datetime
from app.forms import ResetPasswordForm
from app.forms import ProductForm
import base64
import os
from werkzeug.utils import secure_filename
from flask import current_app


# Blueprint for routes
bp = Blueprint('main', __name__)

# Basket page route
@bp.route('/basket')
@login_required
def basket():
    return render_template('basket.html')

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
        appointment_dt = datetime.combine(form.date.data, form.time.data)
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




# Password reset request (user enters email)
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)  # pass full User object
        flash('Check your email for instructions to reset your password.')
        return redirect(url_for('main.login_route'))
    return render_template('reset_password_request.html', form=form)

# Password reset with token
@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Invalid or expired token')
        return redirect(url_for('main.home'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('main.login_route'))

    return render_template('reset_password.html', form=form)


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

    upcoming_bookings = Booking.query.filter(
        Booking.appointment_datetime >= datetime.utcnow()).count()

    past_bookings = total_bookings - upcoming_bookings

    recent = Booking.query.order_by(Booking.id.desc()).limit(10).all()

    return render_template(
        'admin_dashboard.html',
        total=total_bookings,
        upcoming=upcoming_bookings,
        past=past_bookings,
        recent=recent
    )

@bp.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_manage_users():
    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        user = User.query.get_or_404(user_id)

        if action == 'edit':
            user.username = request.form['username']
            user.email = request.form['email']
            user.is_admin = 'is_admin' in request.form
            new_password = request.form.get('new_password')
            if new_password:
                user.set_password(new_password)
                flash('Password updated for user.')
            flash('User updated successfully.')

        elif action == 'delete':
            if user.id == current_user.id:
                flash('You cannot delete yourself.', 'danger')
            else:
                db.session.delete(user)
                flash('User deleted successfully.')

        db.session.commit()
        return redirect(url_for('main.admin_manage_users'))

    users = User.query.all()
    return render_template('admin_manage_users.html', users=users)
<<<<<<< HEAD

# Admin: List all products
@bp.route('/admin/products')
@login_required
def admin_products():
    if not current_user.is_admin:
        abort(403)
    products = Product.query.all()
    return render_template('admin_products.html', products=products)

# Admin: Add product
# Admin: Add product
@bp.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        abort(403)

    form = ProductForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            # Secure the filename
            filename = secure_filename(form.image.data.filename)
            # Ensure unique filename (prepend timestamp)
            import time
            filename = f"{int(time.time())}_{filename}"
            # Save to static/images/
            image_path = os.path.join(current_app.root_path, 'static', 'images', filename)
            form.image.data.save(image_path)

        product = Product(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            price=form.price.data,
            image_filename=filename if filename else "default.png"  # fallback image
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully.')
        return redirect(url_for('main.admin_products'))

    return render_template('admin_product_form.html', form=form, action='Add')


# Admin: Edit product
@bp.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        abort(403)

    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            import time
            filename = f"{int(time.time())}_{filename}"
            image_path = os.path.join(current_app.root_path, 'static', 'images', filename)
            form.image.data.save(image_path)
            product.image_filename = filename  # update filename in DB

        product.name = form.name.data
        product.description = form.description.data
        product.category = form.category.data
        product.price = form.price.data
        db.session.commit()
        flash('Product updated successfully.')
        return redirect(url_for('main.admin_products'))

    return render_template('admin_product_form.html', form=form, action='Edit', product=product)

# Admin: Delete product
@bp.route('/admin/product/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        abort(403)
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully.')
    return redirect(url_for('main.admin_products'))

=======
>>>>>>> 1969204fdda817d81c68babfa45e1616e2ca350e
