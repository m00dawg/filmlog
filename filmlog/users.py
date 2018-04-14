from flask import request, render_template, redirect, url_for, flash, abort
from sqlalchemy.sql import select, text, func
import os, re
from flask_login import LoginManager, login_user, logout_user, UserMixin

from werkzeug.security import generate_password_hash, \
     check_password_hash

from filmlog import app
from filmlog import database
from filmlog import functions

engine = database.engine

class User(UserMixin):
    def __init__(self, userID):
        self.id = userID

    def get_id(self):
        return unicode(self.id)

    def get(userID):
        return self.id

    def set_password(self, password_cleartest):
        self.password = generate_password_hash(password_cleartest)

    def check_password(self, password):
        return check_password_hash(self.password, password)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect("/login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        qry = text("""SELECT userID, password FROM Users
                WHERE username = :username""")
        user = engine.execute(qry, username=username).fetchone()
        if user:
            if check_password_hash(user.password, password):
                login_user(User(user.userID))
                return redirect("/")
    return render_template('users/login.html')

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect("/")
