from flask import Flask, render_template, request, flash, redirect
from models import connect_db
from forms import SignupForm, LoginForm

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///capstone"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = 'password'

connect_db(app)

#################################### Routes ####################################


@app.route('/')
def show_home():
    """Show homepage"""

    return render_template('home.html')


@app.route('/signup')
def signup_user():
    """Signup a new user via class method, save hashed password to database"""

    form = SignupForm()

    if form.validate_on_submit():
        print('success')
    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Authenticate user via vlass method and login"""

    form = LoginForm()

    if form.validate_on_submit():
        print('success')
    else:
        return render_template('login.html', form=form)
