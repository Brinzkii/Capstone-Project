from flask import Flask, render_template, request, flash, redirect, session, g
from sqlalchemy.exc import IntegrityError
from models import connect_db, db, User, User, Drink, Ingredient, DrinkIngredients, Glass, Category, Favorite, Comment
from forms import SignupForm, LoginForm

app = Flask(__name__)

CURR_USER_KEY = ''

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///capstone"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = 'password'

connect_db(app)

#################################### User Routes ####################################


@app.context_processor
def inject_categories():
    """Make categories available in base template for use in header"""

    categories = Category.query.order_by(Category.name).all()
    return dict(categories=categories)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def sess_login(user):
    """Add user to session"""

    session[CURR_USER_KEY] = user.id


def sess_logout():
    """Remove user from session"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def show_home():
    """Show homepage"""

    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup_user():
    """Signup a new user via class method, save hashed password to database"""

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(username=form.username.data,
                               password=form.password.data, profile_img=form.profile_img.data)
            db.session.commit()
            sess_login(user)
            flash(f"Welcome to the club, {user.username}!", 'success')
            return redirect('/')
        except IntegrityError:
            flash('Sorry, that username is already taken!', 'danger')
            return render_template('signup.html', form=form)
    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Authenticate user via vlass method and login"""

    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = User.authenticate(
                username=form.username.data, password=form.password.data)
            sess_login(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect('/')
        except:
            flash('Sorry, please try again!', 'danger')
            return render_template('login.html', form=form)
    else:
        return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    """Log a user out"""

    sess_logout()
    flash(f'{g.user.username} has now been logged out.', 'warning')
    return redirect('/')

#################################### Drink Routes ####################################


@app.route('/drinks')
def show_drinks():
    """Show all drinks in database"""

    drinks = Drink.query.all()

    return render_template('drinks.html', drinks=drinks, title='All Drinks')


@app.route('/<int:drink_id>')
def show_drink_details(drink_id):
    """Show details for a specific drink"""

    drink = Drink.query.get_or_404(drink_id)
    ingredients = drink.ingredients

    return render_template('drink-details.html', drink=drink, ingredients=ingredients, Ingredient=Ingredient)


@app.route('/drinks/<int:category_id>')
def show_category_drinks(category_id):
    """Show all drinks in a category"""

    category = Category.query.get_or_404(category_id)
    drinks = category.drinks

    return render_template('drinks.html', drinks=drinks, title=f"{category.name}")
