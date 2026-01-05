from flask import Blueprint, render_template, flash, redirect, url_for, request, session, abort
from urllib.parse import urlsplit
from app import db, login
from app.forms import LoginForm, RegistrationForm, FootprintForm, BookingForm, SettingsForm, ChangePasswordForm, SupportForm, BookingRescheduleForm, EnergyEntryForm, EnergyGoalForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app.models import User, Booking, Product, Basket, BasketItem, SupportMessage, EnergyEntry, EnergyGoal
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
    # Ensure basket exists for user
    basket = db.session.scalar(sa.select(Basket).where(Basket.user_id == current_user.id))
    if basket:
        # compute total and prepare items for template
        total = 0
        items = []
        for it in basket.items:
            prod = it.product
            price = prod.price * (it.quantity or 1)
            total += price
            items.append({'id': it.id, 'name': prod.name, 'quantity': it.quantity, 'price': f"£{prod.price:.2f}", 'total': f"£{price:.2f}"})
        return render_template('basket.html', basket={'items': items, 'total_price': f"£{total:.2f}"})
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


@bp.route('/basket/add/<int:product_id>')
@login_required
def add_to_basket(product_id):
    product = Product.query.get_or_404(product_id)
    basket = db.session.scalar(sa.select(Basket).where(Basket.user_id == current_user.id))
    if not basket:
        basket = Basket(user_id=current_user.id)
        db.session.add(basket)
        db.session.commit()

    # check if item exists
    item = db.session.scalar(sa.select(BasketItem).where(BasketItem.basket_id == basket.id).where(BasketItem.product_id == product.id))
    if item:
        item.quantity = (item.quantity or 1) + 1
    else:
        item = BasketItem(basket_id=basket.id, product_id=product.id, quantity=1)
        db.session.add(item)

    db.session.commit()
    flash(f'Added {product.name} to your basket.')
    return redirect(url_for('main.green_products'))


@bp.route('/basket/remove/<int:item_id>', methods=['POST', 'GET'])
@login_required
def remove_from_basket(item_id):
    item = BasketItem.query.get_or_404(item_id)
    if not item.basket or item.basket.user_id != current_user.id:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('Item removed from basket.')
    return redirect(url_for('main.basket'))

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

@bp.route('/energy_tracker', methods=['GET', 'POST'])
@login_required
def energy_tracker():
    entry_form = EnergyEntryForm()
    goal_form = EnergyGoalForm()

    # Add new energy entry
    if entry_form.validate_on_submit() and entry_form.submit.data:
        entry = EnergyEntry(user_id=current_user.id, entry_date=entry_form.entry_date.data, kwh=entry_form.kwh.data)
        db.session.add(entry)
        db.session.commit()
        flash('Energy entry added.')
        return redirect(url_for('main.energy_tracker'))

    # Save/Update goal
    if goal_form.validate_on_submit() and goal_form.submit.data:
        goal = db.session.scalar(sa.select(EnergyGoal).where(EnergyGoal.user_id == current_user.id))
        if not goal:
            goal = EnergyGoal(user_id=current_user.id, daily_kwh_goal=goal_form.daily_kwh_goal.data)
            db.session.add(goal)
        else:
            goal.daily_kwh_goal = goal_form.daily_kwh_goal.data
        db.session.commit()
        flash('Daily energy goal saved.')
        return redirect(url_for('main.energy_tracker'))

    # Load user's entries and goal
    entries = db.session.scalars(sa.select(EnergyEntry).where(EnergyEntry.user_id == current_user.id).order_by(EnergyEntry.entry_date.desc())).all()
    goal = db.session.scalar(sa.select(EnergyGoal).where(EnergyGoal.user_id == current_user.id))

    # Simple tips based on latest entry
    tips = []
    latest = entries[0] if entries else None
    if latest:
        if latest.kwh > (goal.daily_kwh_goal or 0):
            tips.append('Your latest day is above your goal — consider reducing appliance usage.')
        else:
            tips.append('You are within your goal — keep up the good work!')

    # Summarize weekly average (last 7 entries by date)
    recent = entries[:7]
    avg = None
    if recent:
        avg = round(sum(e.kwh for e in recent) / len(recent), 2)

    return render_template('energy_tracker.html', entry_form=entry_form, goal_form=goal_form, entries=entries, goal=goal, tips=tips, weekly_avg=avg)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    settings_form = SettingsForm(obj=current_user)
    pwd_form = ChangePasswordForm()
    support_form = SupportForm()

    # Update basic settings
    if settings_form.validate_on_submit():
        current_user.name = settings_form.name.data
        current_user.email = settings_form.email.data
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('main.settings'))

    # Change password
    if pwd_form.validate_on_submit():
        if not current_user.check_password(pwd_form.current_password.data):
            flash('Current password incorrect.', 'danger')
        else:
            current_user.set_password(pwd_form.password.data)
            db.session.commit()
            flash('Password changed successfully.')
        return redirect(url_for('main.settings'))
    # Send support message
    if support_form.validate_on_submit():
        msg = SupportMessage(user_id=current_user.id, subject=support_form.subject.data, message=support_form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash('Support message sent. Our team will contact you shortly.')
        return redirect(url_for('main.settings'))

    # User bookings to manage
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.appointment_datetime.desc()).all()
    return render_template('settings.html', settings_form=settings_form, pwd_form=pwd_form, support_form=support_form, bookings=user_bookings)


@bp.route('/booking/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    db.session.delete(booking)
    db.session.commit()
    flash('Booking cancelled.')
    return redirect(url_for('main.settings'))


@bp.route('/booking/reschedule/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def reschedule_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    form = BookingRescheduleForm()
    if form.validate_on_submit():
        new_dt = datetime.combine(form.date.data, form.time.data)
        # check conflict
        conflict = Booking.query.filter(Booking.appointment_datetime == new_dt).filter(Booking.id != booking.id).first()
        if conflict:
            flash('There is already a booking at that date/time. Please choose another.', 'danger')
            return redirect(url_for('main.reschedule_booking', booking_id=booking.id))
        booking.appointment_datetime = new_dt
        db.session.commit()
        flash('Booking rescheduled.')
        return redirect(url_for('main.settings'))
    return render_template('reschedule_booking.html', form=form, booking=booking)


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

