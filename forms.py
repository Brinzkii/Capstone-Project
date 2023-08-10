# from app import app
from models import db, Ingredient
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    TextAreaField,
    SelectField,
    FieldList,
    FormField,
)
from wtforms.validators import DataRequired, Email, Length


class SignupForm(FlaskForm):
    """Form for signing up new user"""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password (6 char min)", validators=[Length(min=6)])
    profile_img = StringField("Profile Image (optional)")


class LoginForm(FlaskForm):
    """Form for logging in existing user"""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=6)])


class SearchForm(FlaskForm):
    """Form for searching database"""

    search = StringField("Search")


class DrinkForm(FlaskForm):
    """Form for adding drink to database"""

    name = StringField("Name", validators=[DataRequired()])
    category_id = SelectField("Category", validators=[DataRequired()])
    glass_id = SelectField("Glass", validators=[DataRequired()])
    instructions = TextAreaField("Instructions", validators=[DataRequired()])
    main_img = StringField("Main Image (url)", validators=[DataRequired()])
    thumbnail = StringField("Thumbnail (url - optional)")
    video = StringField("Video (url - optional)")


class IngredientsForm(FlaskForm):
    """Form for allowing selection of multiple ingredients"""

    ingredient1 = SelectField("Ingredient", validators=[DataRequired()])
    measurement1 = StringField("Measurement", validators=[DataRequired()])
    ingredient2 = SelectField("Ingredient", validators=[DataRequired()])
    measurement2 = StringField("Measurement", validators=[DataRequired()])
    ingredient3 = SelectField("Ingredient")
    measurement3 = StringField("Measurement")
    ingredient4 = SelectField("Ingredient")
    measurement4 = StringField("Measurement")
    ingredient5 = SelectField("Ingredient")
    measurement5 = StringField("Measurement")
    ingredient6 = SelectField("Ingredient")
    measurement6 = StringField("Measurement")
    ingredient7 = SelectField("Ingredient")
    measurement7 = StringField("Measurement")
    ingredient8 = SelectField("Ingredient")
    measurement8 = StringField("Measurement")
    ingredient9 = SelectField("Ingredient")
    measurement9 = StringField("Measurement")
    ingredient10 = SelectField("Ingredient")
    measurement10 = StringField("Measurement")
    ingredient11 = SelectField("Ingredient")
    measurement11 = StringField("Measurement")
    ingredient12 = SelectField("Ingredient")
    measurement12 = StringField("Measurement")
    ingredient13 = SelectField("Ingredient")
    measurement13 = StringField("Measurement")
    ingredient14 = SelectField("Ingredient")
    measurement14 = StringField("Measurement")
    ingredient15 = SelectField("Ingredient")
    measurement15 = StringField("Measurement")


class CommentForm(FlaskForm):
    """Form for adding comment to drink recipe"""

    comment = TextAreaField("What would you like to say?", validators=[DataRequired()])
