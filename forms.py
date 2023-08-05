from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class SignupForm(FlaskForm):
    """Form for signing up new user"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password (6 char min)',
                             validators=[Length(min=6)])
    profile_img = StringField('Profile Image (optional)')


class LoginForm(FlaskForm):
    """Form for logging in existing user"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class SearchForm(FlaskForm):
    """Form for searching database"""

    search = StringField('Search')
