from app import app
from models import Drink, Ingredient, Glass, Category, DrinkIngredient, db
from time import sleep
from alive_progress import alive_bar
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

    with alive_bar(len(categories['drinks']), title='Adding categories:', length=25) as bar:
        for category in categories["drinks"]:
            c = Category(name=category["strCategory"].title())

            with app.app_context():
                db.session.add(c)
                db.session.commit()
                bar()
                

def add_glasses():
    """Get all glass types"""

    resp = requests.get(base_url + "list.php", params={"g": "list"})
    glasses = resp.json()

    with alive_bar(len(glasses['drinks']), title='Adding glasses:', length=25) as bar:
        for glass in glasses["drinks"]:
            g = Glass(name=glass["strGlass"].title())

            with app.app_context():
                db.session.add(g)
                db.session.commit()
                bar()


def add_ingredients():
    """Get all ingredients"""

    resp = requests.get(base_url + "list.php", params={"i": "list"})
    ingredients = []
    ingredients_raw = resp.json()

    # First get list of all ingredients
    for ingredient in ingredients_raw["drinks"]:
        ingredients.append(ingredient["strIngredient1"])

    # Now query each for details and add to DB
    with alive_bar(len(ingredients), title='Adding ingredients:', length=25) as bar:
        ing_list = []
        for ingredient in ingredients:
            resp = requests.get(base_url + "search.php", params={"i": f"{ingredient}"})
            ings = resp.json()

            i = Ingredient(
                name=ings["ingredients"][0]["strIngredient"].title(),
                description=ings["ingredients"][0]["strDescription"],
                abv=ings["ingredients"][0]["strABV"],
                img=f"https://www.thecocktaildb.com/images/ingredients/{ings['ingredients'][0]['strIngredient']}.png",
            )

            ing_list.append(i)
            bar()

        with app.app_context():
            db.session.add_all(ing_list)
            db.session.commit()


def add_all_drinks():
    """Query all drinks by category"""

    with app.app_context():
        categories = Category.query.all()
        glasses = Glass.query.all()

        # Get a list of all drinks in a category
        with alive_bar(len(categories), length=25) as bar:
            for category in categories:
                bar.title = f'Adding {category.name} drinks:'
                resp = requests.get(
                    base_url + "filter.php", params={"c": f"{category.name}"}
                )
                drinks = resp.json()

                # Get the details of each drink in the list we just received
                count = 0
                drink_list = []
                while count <= len(drinks["drinks"]) - 1:
                    # Create drink object
                    d = Drink(
                        name=drinks["drinks"][count]["strDrink"],
                        api_id=drinks["drinks"][count]["idDrink"],
                        image=drinks["drinks"][count]["strDrinkThumb"],
                    )

                    count += 1
                    drink_list.append(d)

                db.session.add_all(drink_list)
                db.session.commit()
                bar()

        # Get a list of all drinks that use a particular glass
        with alive_bar(len(glasses), length=25) as bar:
            for glass in glasses:
                bar.title = f'Adding {glass.name} drinks:'
                resp = requests.get(
                    base_url + "filter.php", params={"g": f"{glass.name}"}
                )
                drinks = resp.json()

                # If drink not already in database get the details and add to database
                count = 0
                drink_list = []
                while count <= len(drinks['drinks']) - 1:
                    # Check if in database already
                    if Drink.query.filter_by(name=drinks["drinks"][count]["strDrink"]).first():
                        count += 1
                    else:
                        d = Drink(
                        name=drinks["drinks"][count]["strDrink"],
                        api_id=drinks["drinks"][count]["idDrink"],
                        image=drinks["drinks"][count]["strDrinkThumb"],
                    )

                        count += 1
                        drink_list.append(d)
                        

                db.session.add_all(drink_list)
                db.session.commit()
                bar()

        


def add_drink_ingredients():
    """
    Adds additional drink details and creates an entry for each ingredient tying ingredient to drink with measurement
    """

    with app.app_context():
        drinks = Drink.query.all()

        # Get detailed info for each drink in database via API and update missing info
        with alive_bar(len(drinks), length=20, title_length=20) as bar:
            for drink in drinks:
                bar.title = f'Adding {drink.name}:'
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
                category = Category.query.filter_by(name=data["strCategory"].title()).first()

                drink.video = data["strVideo"]
                drink.category_id = category.id
                drink.glass_id = glass.id
                drink.instructions = data["strInstructions"]

                # Loop through ingredients and create pairs in DB, adding ingredients if they are missing
                count = 1
                drink_ings = []
                while data[f"strIngredient{count}"] != None:
                    ingredient = Ingredient.query.filter_by(
                        name=data[f"strIngredient{count}"].title()
                    ).first()

                    if ingredient == None:
                        i = Ingredient(name=data[f"strIngredient{count}"].title())

                        db.session.add(i)
                        db.session.commit()

                        d_i = DrinkIngredient(
                            drink_id=drink.id,
                            ingredient_id=i.id,
                            measurement=data[f"strMeasure{count}"],
                        )

                        drink_ings.append(d_i)
                    else:
                        d_i = DrinkIngredient(
                            drink_id=drink.id,
                            ingredient_id=ingredient.id,
                            measurement=data[f"strMeasure{count}"],
                        )

                        drink_ings.append(d_i)

                    db.session.add_all(drink_ings)
                    db.session.commit()

                    count += 1
                bar()


add_categories()

print(
"""

*********************************************************************************

Categories successfully stored - glasses will begin in 5 seconds

*********************************************************************************

"""
)
sleep(5)

add_glasses()

print(
"""

*********************************************************************************

Glasses successfully stored - ingredients will begin in 5 seconds

*********************************************************************************

"""
)
sleep(5)

add_ingredients()

print(
"""

*********************************************************************************

Ingredients successfully stored - drinks will begin in 5 seconds

*********************************************************************************

"""
)
sleep(5)

add_all_drinks()

print(
"""

*********************************************************************************

Drinks successfully stored - Additional drink details and ingredients for all will begin in 10 seconds

                                  ETA ~ 35 mins                                  

*********************************************************************************

"""
)
sleep(10)

add_drink_ingredients()

print(
"""

*********************************************************************************

Database successfully seeded!

*********************************************************************************

"""
)
