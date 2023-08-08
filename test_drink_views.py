import os
from models import db
from unittest import TestCase
from flask import g
from models import db, User, Drink, Category, Glass, Favorite, Comment, Ingredient

os.environ["DATABASE_URL"] = "postgresql:///capstone-test"

from app import app, CURR_USER_KEY

app.config['TESTING'] = True
app.config["WTF_CSRF_ENABLED"] = False

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_drink_views.py


class TestDrinkViews(TestCase):
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
            # Create test ingredient
            i = Ingredient(name='test-ingredient')

            db.session.add(c)
            db.session.add(g)
            db.session.add(i)
            db.session.commit()

            # Create test drink
            d1 = Drink(name='drink1', category_id=c.id, glass_id=g.id, instructions='test instructions',
              thumbnail='test-thumb.jpg', main_img='test-main.jpg')
            d2 = Drink(name='drink2', category_id=c.id, glass_id=g.id, instructions='test instructions',
              thumbnail='test-thumb.jpg', main_img='test-main.jpg')
            d3 = Drink(name='drink3', category_id=c.id, glass_id=g.id, instructions='test instructions',
              thumbnail='test-thumb.jpg', main_img='test-main.jpg')

            db.session.add(d1)
            db.session.add(d2)
            db.session.add(d3)
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


    def test_drinks_view(self):
        """Test view for showing all drinks in db while not logged in"""

        resp = self.client.get('/drinks')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('All Drinks', html)
        self.assertIn('drink1', html)
        self.assertIn('drink2', html) 
        self.assertIn('drink3', html)
        self.assertNotIn('i class="bi', html)


    def test_drinks_view_user(self):
        """Test view for showing all drinks while logged in
        
        Should show favorite buttons and a button to add drinks
        """

        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    user = User.query.filter_by(username='test-user').first()
                    sess[CURR_USER_KEY] = user.id

            resp = c.get('/drinks')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('All Drinks', html)
            self.assertIn('Get Started', html)
            self.assertIn('i class="bi', html) 


    def test_drinks_add_view(self):
        """Test view for adding a drink while not logged in"""

        resp = self.client.get('/drinks/add')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Enter Drink Details', html)
        self.assertIn('<select', html)
        self.assertIn('<textarea', html) 

        resp = self.client.post('/drinks/add', data={
            'name':'test-name', 'category_id': 1, 'glass_id': 1, 'instructions': 'test instructions', 'thumbnail': 'thumb.img', 'main_img': 'main.img'
            }, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Warning', html)
        self.assertIn('must be logged in to add a drink', html)


    def test_drinks_add_view_user(self):
        """Test view for adding a drink while logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    user = User.query.filter_by(username='test-user').first()
                    sess[CURR_USER_KEY] = user.id

        resp = self.client.post('/drinks/add', data={
            'name':'test-name', 'category_id': 1, 'glass_id': 1, 'instructions': 'test instructions', 'thumbnail': 'thumb.img', 'main_img': 'main.img'
            }, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Info', html)
        self.assertIn('enter the drink ingredients and their measurements', html)  
        self.assertIn('Add test-name Ingredients and Measurements', html)  


################################ WIP ###################################
    def test_ingredients_add_view(self):
        """Test view for adding ingredients for user drink"""

        with app.app_context():
            drink = Drink.query.first()
            ingredient = Ingredient.query.first()

        resp = self.client.get(f'/{drink.id}/ingredients/add')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<select', html)  
        self.assertIn(f'Add {drink.name} Ingredients and Measurements', html) 

        resp = self.client.post(f'/{drink.id}/ingredients/add', data={
            'ingredient1': ingredient.id, 'measurement1': 1, 'ingredient2': ingredient.id, 'measurement2': 1
                                                                      }, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Danger', html)  
        self.assertIn('must be logged in to access', html) 
