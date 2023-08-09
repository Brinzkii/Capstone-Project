import os
from models import db
from unittest import TestCase
from flask import g
from models import db, User, Drink, Category, Glass, Favorite, Comment, Ingredient, DrinkPost

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
        self.assertIn('warning', html)
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
        self.assertIn('info', html)
        self.assertIn('enter the drink ingredients and their measurements', html)  
        self.assertIn('Add test-name Ingredients and Measurements', html)  


    def test_ingredients_add_view(self):
        """Test view for adding ingredients for user drink"""

        with app.app_context():
            i = Ingredient(name='another-test-ingredient')
            db.session.add(i)
            db.session.commit()
            drink = Drink.query.first()
            ingredients = Ingredient.query.all()

        resp = self.client.get(f'/{drink.id}/ingredients/add')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<select', html)  
        self.assertIn(f'Add {drink.name} Ingredients and Measurements', html)


        resp = self.client.post(f'/{drink.id}/ingredients/add', data={
            'ingredient1': ingredients[0].id, 'measurement1': 1, 'ingredient2': ingredients[1].id, 'measurement2': 1
                                                                      }, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('danger', html)  


    def test_ingredients_add_view_user(self):
        """Test view for adding ingredients for user drink"""

        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    user = User.query.filter_by(username='test-user').first()
                    sess[CURR_USER_KEY] = user.id
                    drink = Drink.query.filter_by(name='drink1').first()

                    d_p = DrinkPost(drink_id=drink.id, user_id=sess[CURR_USER_KEY])
                    i = Ingredient(name='another-test-ingredient')

                    db.session.add(d_p)
                    db.session.add(i)
                    db.session.commit()

                    drink = Drink.query.filter_by(name='drink1').first()
                    ingredients = Ingredient.query.all()

            resp = c.post(f'/{drink.id}/ingredients/add', data={
                'ingredient1': ingredients[0].id, 'measurement1': 1, 'ingredient2': ingredients[1].id, 'measurement2': 1
                                                                      }, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('success', html)


    def test_drink_edit_view(self):
        """Test view for editing a drink while not logged in"""

        with app.app_context():
            drink = Drink.query.first()
            category = Category.query.first()
            glass = Glass.query.first()

        resp = self.client.get(f'/{drink.id}/edit')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Edit', html)
        self.assertIn(drink.name, html)
        self.assertIn('<select', html)

        resp = self.client.post(f'/{drink.id}/edit', data={
            'name': 'test-edit-drink',
            'category_id': category.id,
            'glass_id': glass.id,
            'thumbnail': 'img',
            'main_img': 'img'
        } , follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('warning', html)
        self.assertIn('must be logged in', html)


    def test_drink_edit_view_user(self):
        """Test view for editing a drink while logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    drink = Drink.query.filter_by(name='drink1').first()
                    user = User.query.filter_by(username='test-user').first()
                    sess[CURR_USER_KEY] = user.id

                    d_p = DrinkPost(drink_id=drink.id, user_id=user.id)

                    db.session.add(d_p)
                    db.session.commit()

                    drink = Drink.query.filter_by(name='drink1').first()
                    category = Category.query.first()
                    glass = Glass.query.first()

            resp = c.post(f'/{drink.id}/edit', data={
            'name': 'test-edit-drink',
            'category_id': category.id,
            'glass_id': glass.id,
            'thumbnail': 'img',
            'main_img': 'img'
            } , follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('success', html)
            self.assertIn('changes have been saved', html)


    def test_drink_delete_view(self):
        """Test view for deleting user drink while not logged in"""

        with app.app_context():
            drink = Drink.query.first()

        resp = self.client.get(f'/delete/{drink.id}', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('warning', html)
        self.assertIn('must be logged in', html)


    def test_drink_delete_view_user(self):
        """Test view for deleting a user drink while logged in"""

        # Test if not author of post
        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    drink = Drink.query.filter_by(name='drink1').first()
                    user = User.query.filter_by(username='test-user').first()
                    sess[CURR_USER_KEY] = user.id

            resp = c.get(f'/delete/{drink.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('warning', html)
            self.assertIn('only the author', html)

        # Test if author of post
        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    drink = Drink.query.filter_by(name='drink1').first()
                    user = User.query.filter_by(username='test-user').first()
                    sess[CURR_USER_KEY] = user.id

                    d_p = DrinkPost(drink_id=drink.id, user_id=user.id)

                    db.session.add(d_p)
                    db.session.commit()

                    drink = Drink.query.filter_by(name='drink1').first()

            resp = c.get(f'/delete/{drink.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('warning', html)
            self.assertIn('has now been deleted', html)


    def test_search_view(self):
        """Test view for searching database while not logged in"""

        resp = self.client.post('/search', data={'search': 'drink'}, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('warning', html)
        self.assertIn('must be logged in', html)


    def test_search_view_user(self):
        """Test view for searching database while logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    user = User.query.filter_by(username='test-user').first()
                    sess[CURR_USER_KEY] = user.id
                    drinks = Drink.query.all()

            resp = c.post('/search', data={'search': 'dr'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Search Results', html)
            self.assertIn(drinks[0].name, html)
            self.assertIn(drinks[1].name, html)
            self.assertIn(drinks[2].name, html)


        with self.client as c:
            with c.session_transaction() as sess:
                with app.app_context():
                    user = User.query.filter_by(username='test-user').first()
                    sess[CURR_USER_KEY] = user.id
                    drinks = Drink.query.all()
                    
            resp = c.post('/search', data={'search': 'test-cat'}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Search Results', html)
            self.assertIn(drinks[0].name, html)
            self.assertIn(drinks[1].name, html)
            self.assertIn(drinks[2].name, html)