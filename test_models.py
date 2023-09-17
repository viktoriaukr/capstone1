import os
from unittest import TestCase

from psycopg2 import IntegrityError
from models import db, User, Favorite, Review
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


os.environ["DATABASE_URL"] = "postgresql:///books_lover_tests"


from app import app

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test User model class."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Favorite.query.delete()
        Review.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        response = super().tearDown()
        db.session.rollback()
        return response

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            first_name="Test",
            last_name="User",
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
        )
        db.session.add(u)
        db.session.commit()
        saved_user = User.query.filter_by(username="testuser").first()
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.first_name, "Test")
        self.assertEqual(saved_user.last_name, "User")
        self.assertEqual(saved_user.email, "test@test.com")
        self.assertEqual(saved_user.username, "testuser")

    def test_signup(self):
        """Does User.create successfully create a new user given valid credentials?"""

        user = User.signup(
            "testuser1",
            "test@test1.com",
            "HASHED_PASSWORD",
            "/static/images/default-pic.png",
            "Test",
            "User",
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.username, "testuser1")
        self.assertEqual(user.email, "test@test1.com")
        self.assertEqual(user.image_url, "/static/images/default-pic.png")
        self.assertTrue(bcrypt.check_password_hash(user.password, "HASHED_PASSWORD"))

    def test_failure(self):
        with self.assertRaises(TypeError):
            User.signup("testuser1", "test@test1.com", "HASHED_PASSWORD")

    def test_authentication(self):
        user = User.signup(
            "testuser1",
            "test@test1.com",
            "HASHED_PASSWORD",
            "/static/images/default-pic.png",
            "Test",
            "User",
        )
        db.session.add(user)
        db.session.commit()

        u = User.authenticate("testuser1", "HASHED_PASSWORD")
        self.assertIsNotNone(u)
        self.assertTrue("testuser1", "HASHED_PASSWORD")


class FavoritesTestCase(TestCase):
    """Test favorites model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Favorite.query.delete()
        Review.query.delete()
        user = User(
            first_name="Test",
            last_name="User",
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
        )
        db.session.add(user)
        db.session.commit()
        self.user = user
        self.client = app.test_client()

    def tearDown(self):
        response = super().tearDown()
        db.session.rollback()
        return response

    def test_favorite_model(self):
        fav = Favorite(id=1, status="read", book_id="21", user_id=self.user.id)

        db.session.add(fav)
        db.session.commit()

        favorite = Favorite.query.get(1)

        self.assertEqual(favorite.user_id, self.user.id)
        self.assertEqual(favorite.book_id, "21")
        self.assertEqual(favorite.status, "read")


class ReviewModelTestCase(TestCase):
    """Test review model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Favorite.query.delete()
        Review.query.delete()
        user = User(
            first_name="Test",
            last_name="User",
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
        )
        db.session.add(user)
        db.session.commit()
        self.user = user
        self.client = app.test_client()

    def tearDown(self):
        response = super().tearDown()
        db.session.rollback()
        return response

    def test_review_model(self):
        rev = Review(
            id=1, text="test_text", user_id=self.user.id, book_id="21", user_rating="3"
        )

        db.session.add(rev)
        db.session.commit()

        review = Review.query.get(1)

        self.assertEqual(review.user_id, self.user.id)
        self.assertEqual(review.book_id, "21")
        self.assertEqual(review.text, "test_text")
        self.assertEqual(review.user_rating, 3)
