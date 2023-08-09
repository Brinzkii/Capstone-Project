"""Drink model tests."""

# run these tests like:
#
#    python -m unittest test_drink_model.py

import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Comment, DrinkPost, Favorite, Category, Glass, Ingredient, Drink, DrinkIngredients
from flask import g

os.environ["DATABASE_URL"] = "postgresql:///capstone-test"

from app import app

app.config['TESTING'] = True
app.config["WTF_CSRF_ENABLED"] = False


class TestDrinkModel(TestCase):
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


    def test_drink_model(self):
        """Test drink model"""

        with app.app_context():
            c = Category.query.first()
            g = Glass.query.first()
            d = Drink(name='drink1', category_id=c.id, glass_id=g.id, instructions='test instructions',
                thumbnail='test-thumb.jpg', main_img='test-main.jpg')
            db.session.add(d)
            db.session.commit()
            drink = Drink.query.first()

            self.assertEqual(drink, d)
            self.assertEqual(d.category, c)
            self.assertEqual(d.glass, g)
            self.assertEqual(d.instructions, 'test instructions')


    def test_drink_ingredients(self):
        """Test relationship between drinks and ingredients"""

        with app.app_context():
            ing1 = Ingredient(name='Vodka')
            ing2 = Ingredient(name='Gin')
            db.session.add(ing1)
            db.session.add(ing2)
            db.session.commit()

            c = Category.query.first()
            g = Glass.query.first()
            d = Drink(name='drink1', category_id=c.id, glass_id=g.id, instructions='test instructions',
                thumbnail='test-thumb.jpg', main_img='test-main.jpg')
            
            db.session.add(d)
            db.session.commit()

            d_i = DrinkIngredients(drink_id=d.id, ingredient_id=ing1.id)
            d_i1 = DrinkIngredients(drink_id=d.id, ingredient_id=ing2.id)

            db.session.add(d_i)
            db.session.add(d_i1)
            db.session.commit()

            d = Drink.query.first()

            self.assertIn(ing1, [i.ingredient for i in d.ingredients])
            self.assertIn(d, [d.drink for d in ing1.drinks])
            self.assertEqual(ing1.name, 'Vodka')
            self.assertEqual(ing2.abv, 'N/A')

            Drink.query.delete()

            self.assertFalse(DrinkIngredients.query.first())
