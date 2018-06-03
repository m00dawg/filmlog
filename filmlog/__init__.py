from flask import Flask
from flask import abort, redirect
from sqlalchemy.dialects.mysql import INTEGER, SMALLINT
from datetime import date
from flask_login import LoginManager, UserMixin
import ConfigParser
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect

import os, re


app = Flask(__name__)


config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../config.ini'))

app.secret_key = config.get('session','secret_key')

#app.server_name = config.get('session', 'server_name')

#UPLOAD_FOLDER = config.get('files','upload_folder')
user_files = os.path.join(os.path.abspath(os.path.dirname(__file__)),
    config.get('files', 'user_files'))
# print "DEBUG: " + UPLOAD_FOLDER
#UPLOAD_FOLDER = "/nfs/home/tim/git/filmlog/filmlog/files"
app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = user_files
app.config['THUMBNAIL_SIZE'] = config.get('files', 'thumbnail_size')

# Global CSRF Protection
csrf = CSRFProtect(app)

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
