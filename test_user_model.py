"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Comment, DrinkPost, Favorite, Category, Glass, Ingredient, Drink
from flask import g

os.environ["DATABASE_URL"] = "postgresql:///capstone-test"

from app import app

app.config['TESTING'] = True
app.config["WTF_CSRF_ENABLED"] = False


class TestUserModel(TestCase):
    """Unit tests for UG Mixology user views"""

    def setUp(self):
        """Create test objects and add to test db"""
        
        with app.app_context():
            self.client = app.test_client()

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

            d = Drink(name='drink1', category_id=c.id, glass_id=g.id, instructions='test instructions',
              thumbnail='test-thumb.jpg', main_img='test-main.jpg')
            d2 = Drink(name='drink2', category_id=c.id, glass_id=g.id, instructions='test instructions',
              thumbnail='test-thumb.jpg', main_img='test-main.jpg')
            
            db.session.add(d)
            db.session.add(d2)
            db.session.commit()

    def tearDown(self):
        """Remove session and drop all tables"""

        with app.app_context():
            User.query.delete()
            Drink.query.delete()
            Category.query.delete()
            Glass.query.delete()
            Favorite.query.delete()
            Comment.query.delete()
            DrinkPost.query.delete()
            Ingredient.query.delete()
            db.session.remove()


    def test_user_model(self):
        """Test basic model"""

        with app.app_context():
            u = User(username='dawson', password='password')
            db.session.add(u)
            db.session.commit()
            user = User.query.filter_by(username='dawson').first()

        self.assertEqual(user.username, 'dawson')
        self.assertEqual(user.profile_img, '/static/images/profile.png')
        self.assertEqual(user.password, 'password')


    def test_user_signup(self):
        """Test user model signup method"""

        with app.app_context():
            u = User.signup(username='dawson', password='password', profile_img='')
            db.session.commit()
            user = User.query.filter_by(username='dawson').first()

        # User with no non-unique username
            try:
                with app.app_context():
                    failed_user = User.signup(
                        username='dawson', password="HASHED_PASSWORD", profile_img=""
                    )

                    return db.session.commit()
            except exc.IntegrityError:
                err1 = True
                db.session.rollback()

        # User with short password
            try:
                with app.app_context():
                    failed_user1 = User.signup(
                        username='testuser', password="pwd", profile_img=""
                    )

                    return db.session.commit()
            except ValueError:
                err2 = True
                db.session.rollback()

        
        self.assertEqual(user.username, 'dawson')
        self.assertEqual(user.profile_img, '/static/images/profile.png')
        self.assertIn('$2b$', user.password)
        self.assertTrue(err1)
        self.assertTrue(err2)


    def test_user_authenticate(self):
        """Test user model method for authenticating existing user"""

        with app.app_context():
            u = User.signup(
                username="testuser1",
                password="HASHED_PASSWORD",
                profile_img=''
            )

            db.session.commit()

            self.assertEqual(
                User.authenticate(username="testuser1", password="HASHED_PASSWORD"), u
            )
            self.assertFalse(
                User.authenticate(username="testuser2", password="HASHED_PASSWORD")
            )
            self.assertFalse(
                User.authenticate(username="testuser1", password="HASHED_PASSWOR")
            )


    def test_user_favorite_relation(self):
        """Test relationship between user and favorites"""

        with app.app_context():
            u = User.query.first()
            d = Drink.query.first()
            fav = Favorite(user_id=u.id, drink_id=d.id)
            db.session.add(fav)
            db.session.commit()

            self.assertEqual(d, u.favorites[0].drink)

            db.session.delete(fav)
            db.session.commit()

            self.assertFalse(u.favorites)


    def test_user_comment__relation(self):
        """Test relationship between user and comments"""

        with app.app_context():
            u = User.query.first()
            d = Drink.query.first()
            cmt1 = Comment(user_id=u.id, drink_id=d.id, comment='test comment 1')
            cmt2 = Comment(user_id=u.id, drink_id=d.id, comment='test comment 2')
            db.session.add(cmt1)
            db.session.add(cmt2)
            db.session.commit() 

            self.assertEqual(len(u.comments), 2)
            self.assertEqual(u.comments[0].comment, 'test comment 1')
            self.assertEqual(u.comments[1].comment, 'test comment 2')

            Comment.query.delete()
            db.session.commit()

            self.assertFalse(u.comments)


    def test_user_drinkpost_relation(self):
        """Test relationship between users and drinkposts"""

        with app.app_context():
            u = User.query.first()
            d = Drink.query.all()
            dp1 = DrinkPost(user_id=u.id, drink_id=d[0].id)
            dp2 = DrinkPost(user_id=u.id, drink_id=d[1].id)
            db.session.add(dp1)
            db.session.add(dp2)
            db.session.commit() 

            self.assertEqual(len(u.drinkposts), 2)
            self.assertNotEqual(u.drinkposts[0].drink.name, u.drinkposts[1].drink.name)

       