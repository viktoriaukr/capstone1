from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[Length(min=8)])
    image_url = StringField("(Optional) Image URL")
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])


class LoginForm(FlaskForm):
    """Form for login users."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=8)])


class ReviewForm(FlaskForm):
    """Form for adding review for a book."""

    user_rating = SelectField(
        "Rating", choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
    )
    text = TextAreaField("Comment", validators=[DataRequired()])


class FavoriteForm(FlaskForm):
    """Form for adding favorite books to users private page-list."""

    status = SelectField(
        "Status",
        choices=[
            ("want", "Want to read"),
            ("reading", "Currently reading"),
            ("read", "Read"),
        ],
    )


class EditReviewForm(FlaskForm):
    user_rating = SelectField(
        "Rating", choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
    )
    text = TextAreaField("Comment", validators=[DataRequired()])
