from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from typing import Optional
from app import db, login
import sqlalchemy as sa
import sqlalchemy.orm as so
from . import db

#Admin
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    


#class User(UserMixin, db.Model):
#    id: so.Mapped[int] = so.mapped_column(primary_key=True)
#    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
#    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
#    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
#    is_admin = db.Column(db.Boolean, default=False)

#    def set_password(self, password):
#        self.password_hash = generate_password_hash(password)
#
#    def check_password(self, password):
#        return check_password_hash(self.password_hash, password)

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

class Footprint(db.Model):
    name = db.Column(db.String(100), nullable=False)
    car_emission = db.Column(db.Float(100), nullable=False)
    electricity_usage = db.Column(db.Float(100), nullable=False)