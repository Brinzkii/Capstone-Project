from flask import Flask, render_template, request, flash, redirect
from models import connect_db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///capstone"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = 'password'

connect_db(app)

#################################### Routes ####################################
