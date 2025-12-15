<<<<<<< HEAD
# app/models.py
from datetime import datetime
=======
>>>>>>> fddfc1aa847306ac5fbb88a3306270d248ef156e
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from typing import Optional
<<<<<<< HEAD
from app import db, login
=======
from app import db, login 
>>>>>>> fddfc1aa847306ac5fbb88a3306270d248ef156e
import sqlalchemy as sa
import sqlalchemy.orm as so

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

<<<<<<< HEAD
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
=======
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

>>>>>>> fddfc1aa847306ac5fbb88a3306270d248ef156e
