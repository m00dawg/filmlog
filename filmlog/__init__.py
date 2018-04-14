from flask import Flask
from flask import abort, redirect
from sqlalchemy.dialects.mysql import INTEGER, SMALLINT
from datetime import date
from flask_login import LoginManager, UserMixin
import ConfigParser

import os, re

app = Flask(__name__)

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../config.ini'))

app.secret_key = config.get('session','secret_key')
#app.server_name = config.get('session', 'server_name')

# Views
from filmlog import views

@app.template_filter('to_date')
def _jinja2_filter_date(date, fmt=None):
    if date is None:
        return 'Unknown'
    format='%Y-%m-%d'
    return date.strftime(format)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
