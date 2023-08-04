from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)


class User(db.Model):
    """
    User class model with methods for signing up and authenticating.

    Adds user to session but does not commit for you
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String, unique=True)

    password = db.Column(db.String, nullable=False)

    profile_img = db.Column(db.String, default='/static/images/profile.png')

    @classmethod
    def signup(cls, username, password, profile_img):
        """Sign up a new user"""

        hashed = bcrypt.generate_password_hash(password).decode('UTF-8')

        if profile_img:
            user = User(
                username=username,
                password=hashed,
                profile_img=profile_img
            )
        else:
            user = User(
                username=username,
                password=hashed,
            )

        db.session.add(user)
        return (user)

    @classmethod
    def authenticate(cls, username, password):
        """Checks database for existing user and compares against hashed password"""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Drink(db.Model):
    """Drink class model"""

    __tablename__ = 'drinks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    api_id = db.Column(db.Integer, unique=True)

    name = db.Column(db.String, unique=True)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    glass_id = db.Column(db.Integer, db.ForeignKey('glasses.id'))

    instructions = db.Column(db.String)

    thumbnail = db.Column(db.String)

    main_img = db.Column(db.String)

    video = db.Column(db.String)

    category = db.relationship('Category', backref='drinks')

    glass = db.relationship('Glass', backref='drinks')


class Ingredient(db.Model):
    """Ingredient class model"""

    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String, unique=True)

    description = db.Column(db.String)

    abv = db.Column(db.String, default='N/A')

    img = db.Column(db.String)


class Glass(db.Model):
    """Drink glass class model"""

    __tablename__ = 'glasses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String, unique=True)


class Category(db.Model):
    """Drink categories class model"""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String, unique=True)


class DrinkIngredients(db.Model):
    """Ties ingredients and their measurements to specific cocktails"""

    __tablename__ = 'drink_ingredients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    drink_id = db.Column(db.Integer, db.ForeignKey(
        'drinks.id', ondelete='CASCADE'))

    ingredient_id = db.Column(db.Integer, db.ForeignKey(
        'ingredients.id', ondelete='CASCADE'))

    measurement = db.Column(db.String, default='Personal preference')

    drink = db.relationship('Drink', backref='ingredients')

    ingredient = db.Relationship('Ingredient', backref='drinks')


class Favorite(db.Model):
    """Model for tracking users favorite drinks"""

    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))

    drink_id = db.Column(db.Integer, db.ForeignKey(
        'drinks.id', ondelete='CASCADE'))

    user = db.relationship('User', backref='favorites')


class Comment(db.Model):
    """Model for tracking users favorite drinks"""

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))

    drink_id = db.Column(db.Integer, db.ForeignKey(
        'drinks.id', ondelete='CASCADE'))

    comment = db.Column(db.String, nullable=False)

    user = db.relationship('User', backref='comments')
