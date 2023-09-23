from email.quoprimime import quote
import os
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from fetch import (
    get_books,
    get_authors_details,
    get_ratings_details,
    search,
    author_works,
)
from models import db, connect_db, User, Review, Favorite
from forms import UserAddForm, LoginForm, ReviewForm, FavoriteForm, EditReviewForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.app_context().push()

database_url = os.environ.get("DATABASE_URL", "postgresql:///books_lover")

# Append the host parameter to specify the Unix domain socket path.
database_url += "?host=/tmp"

# Set the modified database URL in your Flask app's configuration.
app.config["SQLALCHEMY_DATABASE_URI"] = database_url

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
# Search for books or authors


@app.route("/search", methods=["POST"])
def search_data():
    """Search for books or authors."""
    args = request.form
    response = args.get("q")
    books = search(response)[:18]
    return render_template("users/show.html", books=books)


###############################################################################################
# Fetch books for a homepage


@app.route("/")
def fetch_books():
    """Fetches books for home page."""
    limit = 18
    data = get_books("/trending/yearly")
    books = data.get("works")[:limit]
    return render_template("home.html", books=books)


@app.route("/<path:key>/<title>", methods=["GET"])
def get_book(key, title):
    """Returns information about one particular book."""
    book = get_books(key)

    if "authors" in book and book["authors"]:
        author = get_authors_details(book["authors"][0]["author"]["key"])
    else:
        author = None

    rating = get_ratings_details(key)
    reviews = Review.query.filter_by(book_id=key).all()
    form = FavoriteForm()
    form2 = ReviewForm()
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


@app.route("/<path:key>/<title>", methods=["POST"])
def book_details(key, title):
    """Allows user to make a comment on a book and gives user ability to add specific book to favorites."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    book = get_books(key)
    form = FavoriteForm()
    form2 = ReviewForm()
    exists = Favorite.query.filter_by(user_id=g.user.id, book_id=key).first()

    if not exists:
        if request.method == "POST" and form.validate_on_submit():
            status = form.status.data
            favorite = Favorite(status=status, book_id=key)
            g.user.favorite.append(favorite)
            db.session.commit()
            flash("Successfully added.", "success")
            return redirect(f"/{key}/{title}")

    if request.method == "POST" and form2.validate_on_submit():
        text = form2.text.data
        user_rating = form2.user_rating.data
        review = Review(text=text, user_rating=user_rating, book_id=key)
        g.user.review.append(review)
        db.session.commit()
        flash("Review added successfully.", "success")
        return redirect(f"/{key}/{title}")

    return render_template("users/book.html", form=form, form2=form2, book=book)


@app.route("/<path:key>/<title>/edit", methods=["GET", "POST"])
def edit_review(key, title):
    """Allows editing of a review."""
    if not g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    review = (
        Review.query.filter(Review.book_id == key)
        .filter(Review.user_id == g.user.id)
        .first()
    )
    if review:
        form = EditReviewForm(obj=review)
        if form.validate_on_submit():
            review.user_rating = form.user_rating.data
            review.text = form.text.data
            db.session.commit()
            flash("Review updated successfully.", "success")
            return redirect(f"/{key}/{title}")

    return render_template("users/edit.html", form=form, review=review)


@app.route("/<path:key>/<title>/delete", methods=["POST"])
def destroy_review(key, title):
    """Delete a review."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    review = (
        Review.query.filter(Review.book_id == key)
        .filter(Review.user_id == g.user.id)
        .first()
    )
    if review:
        db.session.delete(review)
        db.session.commit()

    return redirect(f"/{key}/{title}")


#######################################################################################


@app.route("/my/list")
def list():
    """Shows user's favorite books."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    books = []
    favs = Favorite.query.all()
    for b in favs:
        book_id = b.book_id
        book = get_books(book_id)
        author_key = book["authors"][0]["author"]["key"]
        author = get_authors_details(author_key)
        status = b.status
        books.append({"book": book, "author": author, "status": status})
    return render_template("users/favs.html", books=books)


@app.route("/my/list/delete", methods=["POST"])
def destroy_choice():
    """Allows users to delete books from the favorites."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    books = Favorite.query.all()
    for book in books:
        id = book.id
        data = Favorite.query.get(id)
        print(data)
        db.session.delete(data)
        db.session.commit()
    return redirect("/my/list")


#######################################################################################
# Authors information page


@app.route("/<path:key>/author", methods=["GET", "POST"])
def authors(key):
    """Shows author's details."""
    author = get_authors_details(key)
    data = author_works(key)
    works = data.get("entries")[:10]
    return render_template("users/author.html", author=author, works=works)


########################################################################################
# Error handling
@app.errorhandler(404)
def page_not_found(e):
    """Error handling."""
    return render_template("404.html"), 404
