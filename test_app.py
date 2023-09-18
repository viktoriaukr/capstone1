import os
from unittest import TestCase

from models import db, connect_db, Favorite, User, Review

os.environ["DATABASE_URL"] = "postgresql:///books_lover_tests"

from app import app, CURR_USER_KEY

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False


class AppTestCase(TestCase):
    """Test app routes."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Favorite.query.delete()
        Review.query.delete()

        self.client = app.test_client()

        user = User.signup(
            first_name="John",
            last_name="Smith",
            username="testuser",
            email="test@test.com",
            password="testuser",
            image_url=None,
        )
        db.session.add(user)
        db.session.commit()
        self.testuser = user

        self.user_id = user.id

    def test_search_data(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

                resp = c.post("/search", data={"q": "New Moon"})

                self.assertEqual(resp.status_code, 200)
                self.assertTrue(b"New Moon" in resp.data)

    def test_fetch_books(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                resp = c.get("/")
                self.assertEqual(resp.status_code, 200)

    def test_get_book(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

                resp = c.get("/works/OL1968368W/The_48_Laws_of_Power")

                self.assertEqual(resp.status_code, 200)
                self.assertTrue(b"The 48 Laws of Power" in resp.data)

    def test_book_details(self):
        data = Review(
            text="test_text",
            user_rating=3,
            book_id="/works/OL1968368W",
            user_id=self.testuser.id,
        )
        db.session.add(data)
        db.session.commit()

        data1 = Favorite(
            status="read", user_id=self.testuser.id, book_id="/works/OL1968368W"
        )
        db.session.add(data1)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

                resp = c.post("/works/OL1968368W/The_48_Laws_of_Power")
                self.assertEqual(resp.status_code, 302)

                review = Review.query.one()
                self.assertEqual(review.text, "test_text")

                fav = Favorite.query.one()
                self.assertEqual(fav.status, "read")

    # def test_delete_review(self):
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id

    #             review = Review(
    #                 id=1,
    #                 text="test_text",
    #                 user_rating=2,
    #                 user_id=self.testuser.id,
    #                 book_id="/works/OL1968368W",
    #             )
    #             db.session.add(review)
    #             db.session.commit()

    #             response = c.post(
    #                 "/works/OL1968368W/The_48_Laws_of_Power/delete",
    #                 follow_redirects=True,
    #             )
    #             del_review = Review.query.get(review.id)
    #             self.assertEqual(response.status_code, 200)
    #             self.assertIsNone(del_review)
