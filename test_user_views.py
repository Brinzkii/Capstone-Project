
import os
from models import db
from unittest import TestCase
from flask import Flask
from models import db, User, Drink, Category, Glass, Favorite, Comment

os.environ["DATABASE_URL"] = "postgresql:///capstone-test"

from app import app

app.config['TESTING'] = True
app.config["WTF_CSRF_ENABLED"] = False

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


class TestUserViews(TestCase):
    """Unit tests for UG Mixology user views"""

    def setUp(self):
        """Create test objects and add to test db"""
        
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

            # Create test user
            u = User.signup(username='test-user', password='password', profile_img='')
            # Create test category
            c = Category(name='test-category')
            # Create test glass
            g = Glass(name='test-glass')
            # Create test drink
            d = Drink(name='test-drink', category_id=c.id, glass_id=g.id, instructions='test instructions',
              thumbnail='test-thumb.jpg', main_img='test-main.jpg')

            db.session.add(u)
            db.session.add(c)
            db.session.add(g)
            db.session.commit()

            db.session.add(d)
            db.session.commit()

    def tearDown(self):
        """Remove session and drop all tables"""

        with app.app_context():
            User.query.delete
            Drink.query.delete
            Category.query.delete
            Glass.query.delete
            Favorite.query.delete
            Comment.query.delete
            db.drop_all()
            db.session.remove()


    def test_user_signup(self):
        """
        Test user signup route

        GET request - display signup form

        POST request - create new user, login and redirect
        """

        # Testing GET request
        resp = self.client.get("/signup")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Join the Underground today!', html)

        # Testing POST request
        resp = self.client.post(
            "/signup",
            data={
                "username": "testuser1",
                "password": "password",
                'profile_img': ''
            },
            follow_redirects=True,
        )
        html = resp.get_data(as_text=True)

        with app.app_context():
            user = User.query.filter_by(username="testuser1").first()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user.username, "testuser1")
        self.assertEqual(user.profile_img, "/static/images/profile.png")
        self.assertIn("Welcome to the club", html)
        self.assertIn("Logout", html)
