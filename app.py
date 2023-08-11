from flask import Flask, render_template, request, flash, redirect, session, g
from better_profanity import profanity
from sqlalchemy.exc import IntegrityError
import os
import random
import time
import schedule
import math
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
    DrinkPost,
)
from forms import (
    SignupForm,
    LoginForm,
    SearchForm,
    DrinkForm,
    IngredientsForm,
    CommentForm,
) 

app = Flask(__name__)

CURR_USER_KEY = ""
RESULTS = ''

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///capstone"
)
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
def inject_drink_post():
    """Make posts available in base template for use globally"""

    return dict(DrinkPost=DrinkPost)


@app.context_processor
def inject_search_form():
    """Make search form available in base template for use in header"""

    search_form = SearchForm()
    return dict(search_form=search_form)


@app.context_processor
def inject_check_favorites():
    """Make function for checking drink against favorites available globally"""

    return dict(check_favorites=check_favorites)

@app.context_processor
def inject_len():
    """Make length function available globally"""

    return dict(len=len)

@app.context_processor
def inject_math():
    """Make math library available globally"""

    return dict(math=math)


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
            favorites.append(favs.drink)
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


def get_random_drink():
    """Every 24hrs pick a new drink from database and add to global"""

    drinks = Drink.query.all()
    idx = random.randint(0, len(drinks) - 1)

    return drinks[idx]


@app.route("/")
def show_home():
    """Show homepage - if logged in showcase daily random drink"""

    if g.user:
        drink = get_random_drink()
        return render_template("home.html", drink=drink)
    else:
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
            db.session.rollback()
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
    drinkposts = []

    for favs in user.favorites:
        fav_drink = Drink.query.get_or_404(favs.drink_id)
        favorites.append(fav_drink)

    for posts in user.drinkposts:
        drink = Drink.query.get_or_404(posts.drink_id)
        drinkposts.append(drink)

    return render_template(
        "profile.html", user=user, favorites=favorites, posts=drinkposts
    )


@app.route("/<int:drink_id>/favorite/add")
def add_favorite(drink_id):
    """Add user favorite to database"""

    if g.user:
        f = Favorite(user_id=g.user.id, drink_id=drink_id)

        db.session.add(f)
        db.session.commit()

        flash("Drink successfully added to favorites!", "success")
        return redirect(f"/{drink_id}")
    else:
        flash("You must be logged in to add favorites!", "warning")
        return redirect("/login")


@app.route("/<int:drink_id>/favorite/delete")
def delete_favorite(drink_id):
    """Delete user favorite from database"""

    if g.user:
        f = Favorite.query.filter(
            Favorite.user_id == g.user.id, Favorite.drink_id == drink_id
        ).first()

        db.session.delete(f)
        db.session.commit()

        flash("Drink successfully deleted from favorites", "success")
        return redirect(f"/profile/{g.user.id}")
    else:
        flash("You must be logged in to delete favorites!", "warning")
        return redirect("/login")


@app.route("/<int:drink_id>/comment/add", methods=["GET", "POST"])
def add_comment(drink_id):
    """If loggged in add user comment and censor profanity"""

    form = CommentForm()

    if form.validate_on_submit():
        if g.user:
            censored = profanity.censor(form.comment.data)
            c = Comment(user_id=g.user.id, drink_id=drink_id, comment=censored)

            db.session.add(c)
            db.session.commit()

            flash(f"Your comment was added, {g.user.username}!", "success")
            return redirect(f"/{drink_id}")
        else:
            flash("You must be logged in to leave comments!", "warning")
            return redirect("/login")
    else:
        return render_template("add-comment.html", form=form)


@app.route("/<int:comment_id>/delete")
def delete_comment(comment_id):
    """If logged in delete comment"""

    c = Comment.query.get_or_404(comment_id)

    if g.user and g.user.id == c.user_id:
        db.session.delete(c)
        db.session.commit()

        flash("Your comment has now been deleted!", "success")
        return redirect(f"/{c.drink_id}")
    else:
        flash(
            "You must be logged in and the author of a comment to delete it!", "warning"
        )
        return redirect("/login")


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
        User=User,
        Ingredient=Ingredient,
        DrinkPost=DrinkPost
    )


@app.route("/drinks/<int:category_id>")
def show_category_drinks(category_id):
    """Show all drinks in a category"""

    category = Category.query.get_or_404(category_id)
    drinks = category.drinks

    return render_template("drinks.html", drinks=drinks, title=f"{category.name}")


@app.route("/drinks/add", methods=["GET", "POST"])
def add_drink():
    """Add user drink to database"""

    form = DrinkForm()

    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]
    form.category_id.choices.insert(0, (None, "Select the category"))
    form.glass_id.choices = [
        (g.id, g.name) for g in Glass.query.order_by(Glass.name).all()
    ]
    form.glass_id.choices.insert(0, (None, "Select the glass"))

    if form.validate_on_submit():
        if g.user:
            if form.category_id.data != 'None' and form.glass_id.data != 'None':
                # Create drink from form and add to db
                d = Drink(
                    name=form.name.data,
                    category_id=form.category_id.data,
                    glass_id=form.glass_id.data,
                    instructions=form.instructions.data,
                    main_img=form.main_img.data,
                    thumbnail=form.thumbnail.data or form.main_img.data,
                    video=form.video.data,
                )

                db.session.add(d)
                db.session.commit()

                dp = DrinkPost(user_id=g.user.id, drink_id=d.id)

                db.session.add(dp)
                db.session.commit()

                flash(
                    "Please enter a minimum of two drink ingredients and their measurements to complete the process. If optional measurements/ingredients are missing their conterpart, they will be ignored.",
                    "info",
                )
                return redirect(f"/{d.id}/ingredients/add")
            else:
                flash(
                    "A category and glass must be selected before adding a drink!",
                    "warning",
                )
                return render_template("add-drink.html", form=form)
        else:
            flash('You must be logged in to add a drink!', 'warning')
            return redirect('/login')
    else:
        return render_template("add-drink.html", form=form)


@app.route("/<int:drink_id>/ingredients/add", methods=["GET", "POST"])
def add_ingredients(drink_id):
    """Add ingredients and measurements to go with new drink (max 15 ingredient-measurement pairs)"""
    d = Drink.query.get_or_404(drink_id)
    bad_ans = ['None', None]

    form = IngredientsForm()
    for field in form:
        field.choices = [
            (i.id, i.name) for i in Ingredient.query.order_by(Ingredient.name).all()
        ]
        field.choices[0] = (None, "Select an ingredient")

    if form.validate_on_submit():
        count = 0
        if g.user:
            d_p = DrinkPost.query.filter(DrinkPost.drink_id == d.id, DrinkPost.user_id == g.user.id).first()
            if d_p:
                for field in form:
                    count += 1
                    if "ingredient" in field.id and field.data not in bad_ans:
                        d_i = DrinkIngredients(drink_id=d.id, ingredient_id=field.data)

                    elif "measurement" in field.id and field.data not in bad_ans:
                        if d_i:
                            d_i.measurement = field.data
                            db.session.add(d_i)
                            db.session.commit()
                            d_i = None

                    elif field.data in bad_ans and count >= 5:
                        if count % 2 == 0:
                            flash('Each ingredient must have a measurement!', 'warning')
                            return redirect(f'/{d.id}/ingredients/add')
                    
                        else:
                            flash('Each measurement must have an ingredient!', 'warning')
                            return redirect(f"/{d.id}/ingredients/add")

                    else:
                        flash('Minimum of two ingredients and measurements for a new drink!', 'warning')
                        return redirect(f'/{d.id}/ingredients/add')
            else:
                flash('You must be the author of the drink to edit ingredients!', 'danger')
                return redirect('/')
        else:
            flash('You must be logged in to access this feature!', 'warning')
            return redirect('/')
    else:
        return render_template("add-ingredients.html", form=form, drink=d)


@app.route("/<int:drink_id>/edit", methods=["GET", "POST"])
def edit_drink(drink_id):
    """Show edit drink form if author is g.user and submit changes"""

    drink = Drink.query.get_or_404(drink_id)
    form = DrinkForm(obj=drink)

    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]
    form.category_id.choices.insert(0, (None, "Select the category"))
    form.glass_id.choices = [
        (g.id, g.name) for g in Glass.query.order_by(Glass.name).all()
    ]
    form.glass_id.choices.insert(0, (None, "Select the glass"))

    if form.validate_on_submit():
        if g.user:
            if form.category_id.data != 'None' and form.glass_id.data != 'None':
                if DrinkPost.query.filter(
                    DrinkPost.drink_id == drink_id, DrinkPost.user_id == g.user.id
                ).first():
                    drink.name = form.name.data or drink.name
                    drink.category_id = form.category_id.data or drink.category_id
                    drink.glass_id = form.glass_id.data or drink.glass_id
                    drink.instructions = form.instructions.data or drink.instructions
                    drink.main_img = form.main_img.data or drink.main_img
                    drink.thumbnail = form.thumbnail.data or drink.main_img
                    drink.video = form.video.data or drink.video

                    db.session.add(drink)
                    db.session.commit()

                    flash("Your changes have been saved!", "success")
                    return redirect(f"/{drink.id}")
                else:
                    flash("Sorry, only the author of this drink post can make edits!", "danger")
                    return redirect(f"/")
            else:
                flash(
                    "A category and glass must be selected before adding a drink!",
                    "warning",
                )
                return render_template("edit-drink.html", form=form, drink=drink)
        else:
            flash('You must be logged in to access this feature!', 'warning')
            return redirect('/')
    else:
        return render_template("edit-drink.html", form=form, drink=drink)


@app.route("/delete/<int:drink_id>")
def delete_drink(drink_id):
    """If author is g.user delete drink and redirect to profile"""

    if g.user:
        drink = Drink.query.get_or_404(drink_id)
        post = DrinkPost.query.filter(
            DrinkPost.drink_id == drink_id, DrinkPost.user_id == g.user.id
        ).first()

        if post:
            db.session.delete(drink)
            db.session.delete(post)
            db.session.commit()

            flash(f"{drink.name} has now been deleted!", "warning")
            return redirect(f"/profile/{g.user.id}")
        else:
            flash("Sorry, only the author of this drink post can delete it!", "danger")
            return redirect(f"/")
    else:
        flash('You must be logged in to access this feature!', 'warning')
        return redirect('/')


@app.route("/search", methods=["POST"])
def show_search_results():
    """Query database for any matching drinks, ingredients, categories and display results"""

    form = SearchForm()

    if form.validate_on_submit():
        if g.user:
            q = form.search.data
            results = get_search_results(q)
            
            return render_template(
                "drinks.html",
                drinks=results,
                title=f"{len(results)} Search Results for '{q}'",
            )
        else:
            flash('You must be logged in to access this feature!', 'warning')
        return redirect('/')
    else:
        flash("Something went wrong, please try again!", "warning")
        return redirect("/")


def get_search_results(q):
    """Search DB for input string and return results back to search view"""

    results = []

    # First search for any matching ingredients
    ingredients = Ingredient.query.filter(
        Ingredient.name.ilike(f"%{q}%")).all()
    # Then add each of the drinks containing that ingredient to results array
    if ingredients:
        for ingredient in ingredients:
            for drink in ingredient.drinks:
                if drink.drink != None:
                    results.append(drink.drink)

    # Search for any matching categories
    categories = Category.query.filter(Category.name.ilike(f"%{q}%")).all()
    # Add drinks in matching category to results
    if categories:
        for category in categories:
            for drink in category.drinks:
                if drink != None and drink not in results:
                    results.append(drink)

    # Search for any matching drinks and add to results
    drinks = Drink.query.filter(Drink.name.ilike(f"%{q}%")).all()
    if drinks:
        for drink in drinks:
            if drink != None and drink not in results:
                results.append(drink)

    return results
