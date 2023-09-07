from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User in the system."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    image_url = db.Column(db.Text, default="/static/images/default-placeholder.png")
    password = db.Column(db.Text, nullable=False)
    favorite = db.relationship("Favorite", backref="users")
    review = db.relationship("Review", backref="users")

    @classmethod
    def signup(cls, username, email, password, image_url, first_name, last_name):
        """Sign up user."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            first_name=first_name,
            last_name=last_name,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Favorite(db.Model):
    """User's favorite books"""

    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))
    book_id = db.Column(db.String, nullable=False)
    user = db.relationship("User", backref="favorites")

    def __repr__(self):
        return f"<Favorite #{self.id}: {self.user_id}, {self.book_id}, {self.status}>"


class Review(db.Model):
    """User's comments"""

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(240), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    book_id = db.Column(db.String, nullable=False)
    user_rating = db.Column(db.Integer)
    user = db.relationship("User")


def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)
