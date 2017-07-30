from flask import Flask
from flask import abort
from sqlalchemy.dialects.mysql import INTEGER, SMALLINT
from datetime import date

import os, re
import ConfigParser

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/v1'

# Views
from filmlog import views

# Functions
def result_to_dict(result):
    return [dict(row) for row in result]

@app.template_filter('to_date')
def _jinja2_filter_date(date, fmt=None):
    if date is None:
        return 'Unknown'
    format='%Y-%m-%d'
    return date.strftime(format)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
