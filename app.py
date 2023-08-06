from flask import Flask, render_template, request, flash, redirect, session, g
from sqlalchemy.exc import IntegrityError
from models import (
    connect_db,
    db,
    User,
    User,
    Drink,
    Ingredient,
    DrinkIngredients,
    Glass,
    Category,
    Favorite,
    Comment,
)
from forms import SignupForm, LoginForm, SearchForm

app = Flask(__name__)

CURR_USER_KEY = ""

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///capstone"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = "password"

connect_db(app)

#################################### App Setup Routes ####################################


@app.context_processor
def inject_categories():
    """Make categories available in base template for use in header"""

    categories = Category.query.order_by(Category.name).all()
    return dict(categories=categories)


@app.context_processor
def inject_search_form():
    """Make search form available in base template for use in header"""

    search_form = SearchForm()
    return dict(search_form=search_form)


@app.context_processor
def inject_check_favorites():
    """Make function for checking drink against favorites available globally"""

    return dict(check_favorites=check_favorites)


def check_favorites(drink, favorites):
    """Checks a drink against list of favorite drinks"""

    for fav in favorites:
        if fav == drink:
            return True

    return False


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.before_request
def add_favorites_to_g():
    """If global user exists add favorite drink objects to global"""
    if g.user:
        favorites = []
        for favs in g.user.favorites:
            fav_drink = Drink.query.get_or_404(favs.drink_id)
            favorites.append(fav_drink)
        g.favorites = favorites
    else:
        g.favorites = None


#################################### User Routes ####################################


def sess_login(user):
    """Add user to session"""

    session[CURR_USER_KEY] = user.id


def sess_logout():
    """Remove user from session"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route("/")
def show_home():
    """Show homepage"""

    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup_user():
    """Signup a new user via class method, save hashed password to database"""

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                profile_img=form.profile_img.data,
            )
            db.session.commit()
            sess_login(user)
            flash(f"Welcome to the club, {user.username}!", "success")
            return redirect("/")
        except IntegrityError:
            flash("Sorry, that username is already taken!", "danger")
            return render_template("signup.html", form=form)
    else:
        return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_user():
    """Authenticate user via vlass method and login"""

    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = User.authenticate(
                username=form.username.data, password=form.password.data
            )
            sess_login(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect("/")
        except:
            flash("Sorry, please try again!", "danger")
            return render_template("login.html", form=form)
    else:
        return render_template("login.html", form=form)


@app.route("/logout")
def logout_user():
    """Log a user out"""

    sess_logout()
    flash(f"{g.user.username} has now been logged out.", "warning")
    return redirect("/")


@app.route("/profile/<int:user_id>")
def show_user_profile(user_id):
    """Show user information"""

    user = User.query.get_or_404(user_id)
    favorites = []
    for favs in user.favorites:
        fav_drink = Drink.query.get_or_404(favs.drink_id)
        favorites.append(fav_drink)

    return render_template("profile.html", user=user, favorites=favorites)


#################################### Drink Routes ####################################


@app.route("/drinks")
def show_drinks():
    """Show all drinks in database"""

    drinks = Drink.query.order_by(Drink.name).all()

    return render_template("drinks.html", drinks=drinks, title="All Drinks")


@app.route("/<int:drink_id>")
def show_drink_details(drink_id):
    """Show details for a specific drink"""

    drink = Drink.query.get_or_404(drink_id)
    ingredients = drink.ingredients

    return render_template(
        "drink-details.html",
        drink=drink,
        ingredients=ingredients,
        Ingredient=Ingredient,
    )


@app.route("/drinks/<int:category_id>")
def show_category_drinks(category_id):
    """Show all drinks in a category"""

    category = Category.query.get_or_404(category_id)
    drinks = category.drinks

    return render_template("drinks.html", drinks=drinks, title=f"{category.name}")


@app.route("/search", methods=["POST"])
def show_search_results():
    """Query database for any matching drinks, ingredients, categories and display results"""

    form = SearchForm()

    if form.validate_on_submit():
        q = form.search.data
        results = get_search_results(q)

        return render_template(
            "drinks.html",
            drinks=results,
            title=f"{len(results)} Search Results for '{q}'",
        )
    else:
        flash("Something went wrong, please try again!", "warning")
        return redirect("/")


def get_search_results(q):
    """Search DB for input string and return results back to search view"""

    results = []

    # First search for any matching ingredients
    ingredients = Ingredient.query.filter(Ingredient.name.ilike(f"%{q}%")).all()
    # Then add each of the drinks containing that ingredient to results array
    if ingredients:
        for ingredient in ingredients:
            for drink in ingredient.drinks:
                results.append(drink.drink)

    # Search for any matching categories
    categories = Category.query.filter(Category.name.ilike(f"%{q}%")).all()
    # Add drinnks in matching category to results
    if categories:
        for category in categories:
            results.append(category.drinks)

    # Search for any matching drinks and add to results
    drinks = Drink.query.filter(Drink.name.ilike(f"%{q}%")).all()
    if drinks:
        for drink in drinks:
            results.append(drink)

    return results


@app.route("/favorite/add/<int:drink_id>")
def add_favorite(drink_id):
    """Add user favorite to database"""

    if g.user:
        f = Favorite(user_id=g.user.id, drink_id=drink_id)

        db.session.add(f)
        db.session.commit()

        flash("Drink successfully added to favorites!", "success")
        return redirect(f"/profile/{g.user.id}")
    else:
        flash("You must be logged in to add favorites!", "danger")
        return redirect("/")


@app.route("/favorite/delete/<int:drink_id>")
def delete_favorite(drink_id):
    """Delete user favorite from database"""

    if g.user:
        f = Favorite.query.filter(
            Favorite.user_id == g.user.id, Favorite.drink_id == drink_id
        ).first()

        db.session.delete(f)
        db.session.commit()

        flash("Drink successfully deleted from favorites", "warning")
        return redirect(f"/profile/{g.user.id}")
    else:
        flash("You must be logged in to add favorites!", "danger")
        return redirect("/")
