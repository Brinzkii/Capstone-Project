
from app import app
from models import Drink, Ingredient, Glass, Category, DrinkIngredients, db
import requests

base_url = 'https://www.thecocktaildb.com/api/json/v1/1/'

# with app.app_context():
#     db.drop_all()
#     db.create_all()

# Seed database with data from CocktailAPI


def add_categories():
    """Get all drink categories"""

    resp = requests.get(base_url + 'list.php', params={'c': 'list'})
    categories = resp.json()

    for category in categories['drinks']:
        c = Category(name=category['strCategory'].title())

        with app.app_context():
            db.session.add(c)
            db.session.commit()


def add_glasses():
    """Get all glass types"""

    resp = requests.get(base_url + 'list.php', params={'g': 'list'})
    glasses = resp.json()

    for glass in glasses['drinks']:
        g = Glass(name=glass['strGlass'].title())

        with app.app_context():
            db.session.add(g)
            db.session.commit()


def add_ingredients():
    """Get all ingredients"""

    resp = requests.get(base_url + 'list.php', params={'i': 'list'})
    ingredients = []
    ingredients_raw = resp.json()

    # First get list of all ingredients
    for ingredient in ingredients_raw['drinks']:
        ingredients.append(ingredient['strIngredient1'])

    # Now query each for details and add to DB
    for ingredient in ingredients:
        resp = requests.get(base_url + 'search.php',
                            params={'i': f'{ingredient}'})
        ings = resp.json()

        i = Ingredient(
            name=ings['ingredients'][0]['strIngredient'].title(),
            description=ings['ingredients'][0]['strDescription'],
            abv=ings['ingredients'][0]['strABV'],
            img=f"https://www.thecocktaildb.com/images/ingredients/{ings['ingredients'][0]['strIngredient']}.png"
        )

        with app.app_context():
            db.session.add(i)
            db.session.commit()


def add_all_drinks():
    """Query all drinks by category"""

    with app.app_context():
        categories = Category.query.all()
        all_drinks = []

        # Get a list of all drinks in a category
        for category in categories:
            resp = requests.get(base_url + 'filter.php', params={
                'c': f'{category.name}'
            })
            drinks = resp.json()

            # Get the details of each drink in the list we just received
            for drink in drinks['drinks']:
                resp = requests.get(base_url + 'search.php',
                                    params={'s': f"{drink['strDrink']}"})
                details = resp.json()

                with app.app_context():
                    # Find the drinks glass in our DB
                    glass = Glass.query.filter_by(
                        name=details['drinks'][0]['strGlass'].title()).first()

                    # Create drink object
                    d = Drink(
                        name=details['drinks'][0]['strDrink'],
                        category_id=category.id,
                        glass_id=glass.id,
                        instructions=details['drinks'][0]['strInstructions'],
                        thumbnail=f"{details['drinks'][0]['strDrinkThumb']}/preview",
                        main_img=details['drinks'][0]['strDrinkThumb'],
                        video=details['drinks'][0]['strVideo']
                    )

                    db.session.add(d)
                    db.session.commit()

                    add_drink_ingredients(details['drinks'][0], d)

                    # For each ingredient create a new drink-ingredient entry with measurement


def add_drink_ingredients(drink_resp, drink):
    """Create an entry for each ingredient tying ingredient to drink with measurement"""

    count = 1
    i = drink_resp[f'strIngredient{count}']
    if i != None:
        ingredient = Ingredient.query.filter_by(
            name=i.title()).first()
        d_i = DrinkIngredients(
            drink_id=drink.id,
            ingredient_id=ingredient.id,
            measurement=drink_resp[f'strMeasure{count}']
        )

        db.session.add(d_i)
        db.session.commit()
        count += 1


# add_categories()
# add_glasses()
# add_ingredients()
