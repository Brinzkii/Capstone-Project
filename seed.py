from app import app
from models import Drink, Ingredient, Glass, Category, DrinkIngredients, db
from time import sleep
import random
import requests

base_url = "https://www.thecocktaildb.com/api/json/v1/1/"

with app.app_context():
    db.drop_all()
    db.create_all()

# Seed database with data from CocktailAPI


def add_categories():
    """Get all drink categories"""

    resp = requests.get(base_url + "list.php", params={"c": "list"})
    categories = resp.json()

    for category in categories["drinks"]:
        c = Category(name=category["strCategory"].title())

        with app.app_context():
            db.session.add(c)
            db.session.commit()


def add_glasses():
    """Get all glass types"""

    resp = requests.get(base_url + "list.php", params={"g": "list"})
    glasses = resp.json()

    for glass in glasses["drinks"]:
        g = Glass(name=glass["strGlass"].title())

        with app.app_context():
            db.session.add(g)
            db.session.commit()


def add_ingredients():
    """Get all ingredients"""

    resp = requests.get(base_url + "list.php", params={"i": "list"})
    ingredients = []
    ingredients_raw = resp.json()

    # First get list of all ingredients
    for ingredient in ingredients_raw["drinks"]:
        ingredients.append(ingredient["strIngredient1"])

    # Now query each for details and add to DB
    for ingredient in ingredients:
        resp = requests.get(base_url + "search.php", params={"i": f"{ingredient}"})
        ings = resp.json()

        i = Ingredient(
            name=ings["ingredients"][0]["strIngredient"].title(),
            description=ings["ingredients"][0]["strDescription"],
            abv=ings["ingredients"][0]["strABV"],
            img=f"https://www.thecocktaildb.com/images/ingredients/{ings['ingredients'][0]['strIngredient']}.png",
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
            resp = requests.get(
                base_url + "filter.php", params={"c": f"{category.name}"}
            )
            drinks = resp.json()

            # Get the details of each drink in the list we just received
            count = 0
            while count <= len(drinks["drinks"]) - 1:
                # Create drink object
                d = Drink(
                    name=drinks["drinks"][count]["strDrink"],
                    api_id=drinks["drinks"][count]["idDrink"],
                    category_id=category.id,
                    thumbnail=f"{drinks['drinks'][count]['strDrinkThumb']}/preview",
                    main_img=drinks["drinks"][count]["strDrinkThumb"],
                )

                count += 1

                db.session.add(d)
                db.session.commit()


def add_drink_ingredients(category_id):
    """
    Create an entry for each ingredient tying ingredient to drink with measurement and
    add missing details to drinks.

    Must call one category at a time or the api locks up
    """

    with app.app_context():
        drinks = Drink.query.filter_by(category_id=category_id).all()
        progress = 0

        # Get detailed info for each drink in database via API and update missing info
        for drink in drinks:
            try:
                resp = requests.get(
                    base_url + "lookup.php", params={"i": f"{drink.api_id}"}
                )
            except:
                print("API is mad - waiting 5 seconds")
                sleep(5)

                resp = requests.get(
                    base_url + "lookup.php", params={"i": f"{drink.api_id}"}
                )

            # Add delay to prevent API from locking up
            sleep(random.uniform(2.00, 4.50))

            details = resp.json()
            data = details["drinks"][0]
            glass = Glass.query.filter_by(name=data["strGlass"].title()).first()

            drink.video = data["strVideo"]
            drink.glass_id = glass.id
            drink.instructions = data["strInstructions"]

            progress += 1
            print(
                f"""
 #################  {drink.category.name} ({drink.category.id}/{len(Category.query.all())})  #################
                    
                      Progress: {progress}/{len(drinks)}
-------------------------------------------------------------
                """
            )

            # Loop through ingredients and create pairs in DB, adding ingredients if they are missing
            count = 1
            while data[f"strIngredient{count}"] != None:
                ingredient = Ingredient.query.filter_by(
                    name=data[f"strIngredient{count}"].title()
                ).first()

                if ingredient == None:
                    i = Ingredient(name=data[f"strIngredient{count}"].title())

                    db.session.add(i)
                    db.session.commit()

                    d_i = DrinkIngredients(
                        drink_id=drink.id,
                        ingredient_id=i.id,
                        measurement=data[f"strMeasure{count}"],
                    )

                    db.session.add(d_i)
                else:
                    d_i = DrinkIngredients(
                        drink_id=drink.id,
                        ingredient_id=ingredient.id,
                        measurement=data[f"strMeasure{count}"],
                    )

                    db.session.add(d_i)

                db.session.commit()

                count += 1


add_categories()

print(
    """
*****************************************************************

Categories successfully stored - glasses will begin in 30 seconds

*****************************************************************
      """
)
sleep(30)

add_glasses()

print(
    """
*****************************************************************

Glasses successfully stored - ingredients will begin in 30 seconds

*****************************************************************
      """
)
sleep(30)

add_ingredients()

print(
    """
*****************************************************************

Ingredients successfully stored - drinks will begin in 30 seconds

*****************************************************************
      """
)
sleep(30)

add_all_drinks()

print(
    """
*****************************************************************

Drinks successfully stored - the first category of drink details and ingredients will begin in 30 seconds

*****************************************************************
    """
)
sleep(30)

with app.app_context():
    categories = Category.query.all()
    count = 1

    for category in categories:
        if count == len(categories):
            add_drink_ingredients(category.id)
        else:
            add_drink_ingredients(category.id)
            count += 1

            print(
                """
*****************************************************************

The next category will begin in 60 seconds
                
*****************************************************************              
"""
            )
            sleep(60)

print(
    """
*****************************************************************

Database successfully seeded!

*****************************************************************
      """
)
