
import os
from models import db
from unittest import TestCase
from flask import Flask, g
from models import db, User, Drink, Category, Glass, Favorite, Comment

os.environ["DATABASE_URL"] = "postgresql:///capstone-test"

from app import app, CURR_USER_KEY

app.config['TESTING'] = True
app.config["WTF_CSRF_ENABLED"] = False

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


class TestUserViews(TestCase):
    """Unit tests for UG Mixology user views"""

    def setUp(self):
        """Create test objects and add to test db"""
        
        with app.app_context():
            self.client = app.test_client()

            db.session.expire_on_commit = False
            db.drop_all()
            db.create_all()

            # Create test user
            u = User.signup(username='test-user', password='password', profile_img='')
            # Create test category
            c = Category(name='test-category')
            # Create test glass
            g = Glass(name='test-glass')

            db.session.add(c)
            db.session.add(g)
            db.session.commit()

            # Create test drink
            d = Drink(name='test-drink', category_id=c.id, glass_id=g.id, instructions='test instructions',
              thumbnail='test-thumb.jpg', main_img='test-main.jpg')

            db.session.add(d)
            db.session.commit()

    def tearDown(self):
        """Remove session and drop all tables"""

        with app.app_context():
            g.user = None
            User.query.delete()
            Drink.query.delete()
            Category.query.delete()
            Glass.query.delete()
            Favorite.query.delete()
            Comment.query.delete()
            db.session.remove()


    def test_show_home(self):
        """
        Test home route

        No logged in user - Show welcome content

        Logged in user - show drink of the day
        """

        # Test with no logged in user
        resp = self.client.get('/')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Welcome to Underground Mixology', html)
        self.assertIn('Login', html)
        self.assertIn('Signup', html)

        # Test with a logged in user
        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    user = User.query.filter_by(username='test-user').first()
                    sess[CURR_USER_KEY] = user.id

            resp = c.get("/", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Drink of the Day", html)
            self.assertIn("Likes:", html)
            self.assertIn("Comments:", html)


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


    def test_user_login(self):
        """
        Test user signup route

        GET request - display signup form

        POST request - create new user, login and redirect
        """

        # Testing GET request
        resp = self.client.get("/login")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Please enter your credentials', html)

        # Testing POST request
        resp = self.client.post(
            "/login",
            data={
                "username": "test-user",
                "password": "password",
            },
            follow_redirects=True,
        )
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Success", html)
        self.assertIn("Welcome back, test-user", html)
        self.assertIn("Logout", html)


    def test_user_logout(self):
        """Test logout route"""

        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    user = User.query.filter_by(username='test-user').first()
                    sess[CURR_USER_KEY] = user.id

            resp = c.get("/logout", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test-user has now been logged out", html)


    def test_user_profile(self):
        """
        Test profile route

        Should show user profile pic, favorites and posts      
        """

        with app.app_context():
            user = User.query.filter_by(username='test-user').first()
        
        resp = self.client.get(f'/profile/{user.id}')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("test-user's Profile", html)
        self.assertIn("/static/images/profile.png", html)
        self.assertIn('Favorite Drinks', html)
        self.assertIn('Drink Posts', html)


    def test_user_own_profile(self):
        """
        Test route for own profile
        """

        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    user = User.query.filter_by(username='test-user').first()
                    drink = Drink.query.first()
                    f = Favorite(drink_id=drink.id, user_id=user.id)
                    db.session.add(f)
                    db.session.commit()
                    sess[CURR_USER_KEY] = user.id

            resp = c.get(f'/profile/{user.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test-user's Profile", html)
            self.assertIn("Remove", html)


    def test_add_favorite(self):
        """Test route for adding favorites while logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    user = User.query.filter_by(username='test-user').first()
                    drink = Drink.query.first()
                    sess[CURR_USER_KEY] = user.id

            resp = c.get(f'/{drink.id}/favorite/add', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Success", html)
            self.assertIn("added to favorites", html)
            self.assertIn("test-drink", html)

        # Not logged in
        


    def test_add_favorite_bad(self):
        """Test route for adding favorite if no logged in user"""
        
        with app.app_context():
            drink = Drink.query.first()

        resp = self.client.get(f'/{drink.id}/favorite/add', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Warning', html)
        self.assertIn('must be logged in to add', html)


    def test_delete_favorite(self):
        """Test route for deleting favorite while logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    user = User.query.filter_by(username='test-user').first()
                    drink = Drink.query.first()
                    f = Favorite(drink_id=drink.id, user_id=user.id)
                    db.session.add(f)
                    db.session.commit()
                    drink = Drink.query.first()
                    sess[CURR_USER_KEY] = user.id

            resp = c.get(f'/{drink.id}/favorite/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Success', html)
            self.assertIn('deleted from favorites', html)


    def test_delete_favorite_bad(self):
        """Test route for deleting favorite while not logged in"""

        with app.app_context():
            user = User.query.filter_by(username='test-user').first()
            drink = Drink.query.first()
            f = Favorite(drink_id=drink.id, user_id=user.id)
            db.session.add(f)
            db.session.commit()
            drink = Drink.query.first()

        resp = self.client.get(f'/{drink.id}/favorite/delete', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Warning', html)
        self.assertIn('must be logged in to delete', html)


    def test_add_comment(self):
        """Test route for adding comment while logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    user = User.query.filter_by(username='test-user').first()
                    drink = Drink.query.first()
                    sess[CURR_USER_KEY] = user.id

            # Get Request should show comment form
            resp = c.get(f'/{drink.id}/comment/add', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Enter your comment', html)
            self.assertIn('Add Comment', html)

            # Post request should flash a success message and redirect to drink page 
            resp = c.post(f'/{drink.id}/comment/add', data={'comment': 'test comment'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Success', html)
            self.assertIn('comment was added', html)
            self.assertIn(drink.name, html)


    def test_add_comment_bad(self):
        """Test route for adding comment while not logged in"""

        with app.app_context():
            drink = Drink.query.first()

        resp = self.client.post(f'/{drink.id}/comment/add', data={'comment':'test comment'}, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Warning', html)
        self.assertIn('must be logged in to leave comments', html)


    def test_delete_comment(self):
        """Test route for deletingcomment while logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    user = User.query.filter_by(username='test-user').first()
                    drink = Drink.query.first()
                    cmt = Comment(drink_id=drink.id, user_id=user.id, comment='test comment')
                    db.session.add(cmt)
                    db.session.commit()
                    drink = Drink.query.first()
                    cmt = Comment.query.first()
                    sess[CURR_USER_KEY] = user.id

            # Post request should flash a success message and redirect to drink page 
            resp = c.get(f'/{cmt.id}//delete', data={'comment': 'test comment'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Success', html)
            self.assertIn('comment has now been deleted', html)
            self.assertIn(drink.name, html)


    def test_delete_comment_bad(self):
        """Test route for deleting comment while not logged in"""

        with app.app_context():
            user = User.query.filter_by(username='test-user').first()
            drink = Drink.query.first()
            cmt = Comment(drink_id=drink.id, user_id=user.id, comment='test comment')
            db.session.add(cmt)
            db.session.commit()
            cmt = Comment.query.first()

        resp = self.client.get(f'/{cmt.id}//delete', data={'comment':'test comment'}, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Warning', html)
        self.assertIn('must be logged in and the author of a comment to delete', html)