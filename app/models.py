from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from typing import Optional
from app import db, login
import sqlalchemy as sa
import sqlalchemy.orm as so

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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

