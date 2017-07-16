# TODO
# - Reports

import os
import ConfigParser
from flask import Flask
from flask import request, render_template, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Date, Enum, MetaData, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, SMALLINT
from sqlalchemy.sql import select, text, func
from datetime import date

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini'))

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/v1'

config.get('database', 'url')

app.config['SQLALCHEMY_DATABASE_URI'] = config.get('database', 'url')
engine = create_engine(config.get('database', 'url'), pool_recycle=config.getint('database', 'pool_recycle'))

@app.route('/',  methods = ['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

@app.route('/projects',  methods = ['POST', 'GET'])
def projects():
    if request.method == 'GET':
        qry = text("""SELECT name FROM Projects""")
        projects = engine.execute(qry).fetchall()
        return render_template('projects.html', projects=projects)

@app.route('/project',  methods = ['POST', 'GET'])
def projects():
    if request.method == 'GET':
        qry = text("""SELECT title FROM Films WHERE projectID = :projectID""")
        films = engine.execute(qry, projectID=projectID).fetchall()
        return render_template('projects.html', projects=projects)

@app.route('/filmtypes',  methods = ['GET'])
def film_types():
    if request.method == 'GET':
        qry = text("""SELECT filmTypeID, brand, name, iso, kind
                      FROM FilmTypes
                      JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID""")
        filmtypes = engine.execute(qry).fetchall()
        return render_template('filmtypes.html', filmtypes=filmtypes)
