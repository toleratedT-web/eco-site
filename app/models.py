from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from typing import Optional
from app import db, login 
import sqlalchemy as sa
import sqlalchemy.orm as so
from . import db
from time import time
import jwt
from app import app

#Admin
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        secret = str(app.config['SECRET_KEY'])
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            secret, algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)




@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Booking(db.Model):
    __tablename__ = 'booking'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, sa.ForeignKey('user.id'), nullable=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(120), nullable=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), nullable=False)
    appointment_datetime: so.Mapped[Optional[sa.DateTime]] = so.mapped_column(sa.DateTime, nullable=False)
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.Text, nullable=True)
    created_at: so.Mapped[Optional[sa.DateTime]] = so.mapped_column(sa.DateTime, server_default=sa.func.now())

    def __repr__(self) -> str:
        return f"<Booking {self.id} {self.name} {self.appointment_datetime}>"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'solar', 'ev', 'appliances'
    price = db.Column(db.Float, nullable=False)  # price in your currency


class Basket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    user = db.relationship('User', backref=db.backref('basket', uselist=False))


class BasketItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    basket_id = db.Column(db.Integer, db.ForeignKey('basket.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    product = db.relationship('Product')
    basket = db.relationship('Basket', backref=db.backref('items', lazy='joined'))


class SupportMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=sa.func.now())


class EnergyEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    kwh = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, server_default=sa.func.now())


class EnergyGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    daily_kwh_goal = db.Column(db.Float, nullable=True)