# TODO
# - Reports

from flask import Flask
from flask import abort
#from sqlalchemy import Table, Column, Integer, String, Date, Enum, MetaData, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, SMALLINT
from datetime import date

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/v1'

import os, re
import ConfigParser
from sqlalchemy import create_engine



# Views
import filmlog.views



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
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini'))
    config.get('database', 'url')

    app.config['SQLALCHEMY_DATABASE_URI'] = config.get('database', 'url')
    engine = create_engine(config.get('database', 'url'), pool_recycle=config.getint('database', 'pool_recycle'))

    app.run(host='0.0.0.0')
