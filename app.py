from email.quoprimime import quote
import os
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from fetch import (
    get_books,
    get_authors_details,
    get_ratings_details,
)
from models import db, connect_db, User, Review, Favorite
from forms import UserAddForm, LoginForm, ReviewForm, FavoriteForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.app_context().push()

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///books_lover"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

db.create_all()


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


################################################################
# User Authentication/Registration


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user signup."""

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data,
            )
            db.session.commit()
        except IntegrityError:
            flash("Enter unique username/password", "danger")
            return render_template("users/signup.html", form=form)

        do_login(user)

        return redirect("/")
    else:
        return render_template("users/signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid username/password.", "danger")

    return render_template("users/login.html", form=form)


@app.route("/logout")
def logout():
    """Handle user logout."""

    do_logout()
    flash("You have been successfully logged out.", "success")
    return redirect("/login")


###############################################################################################
# Fetch books for a homepage


@app.route("/")
def fetch_books():
    limit = 18
    data = get_books("/trending/yearly")
    books = data.get("works")[:limit]
    return render_template("home.html", books=books)


@app.route("/<path:key>/<title>", methods=["GET", "POST"])
def book_details(key, title):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = FavoriteForm()
    form2 = ReviewForm()
    reviews = Review.query.filter_by(book_id=key).all()

    if request.method == "POST" and form.validate_on_submit():
        # Handle the form submission for adding the book to favorites
        status = form.status.data
        favorite = Favorite(status=status, book_id=key)
        g.user.favorite.append(favorite)
        db.session.commit()
        flash("Successfully added.", "success")
        return redirect("/my/list")

    if request.method == "POST" and form2.validate_on_submit():
        # Handle the form submission for adding a review
        text = form2.text.data
        user_rating = form2.user_rating.data
        review = Review(text=text, user_rating=user_rating, book_id=key)
        g.user.review.append(review)
        db.session.commit()
        flash("Review added successfully.", "success")
        return redirect(f"/{key}/{title}")

    # Handle the GET request to display book details
    book = get_books(key)
    author_key = book["authors"][0]["author"]["key"]
    author = get_authors_details(author_key)
    rating = get_ratings_details(key)

    return render_template(
        "users/book.html",
        book=book,
        title=title,
        author=author,
        rating=rating,
        reviews=reviews,
        form=form,
        form2=form2,
    )


@app.route("/my/list")
def list():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    books = Favorite.query.all()
    return render_template("users/favs.html", books=books)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
