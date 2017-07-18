# TODO
# - Reports

import os
import ConfigParser
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask import abort
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
        qry = text("""SELECT projectID, name, filmCount, createdOn FROM Projects""")
        projects = engine.execute(qry).fetchall()
        return render_template('projects.html', projects=projects)

@app.route('/projects/<int:projectID>',  methods = ['POST', 'GET'])
def project(projectID):
    if request.method == 'GET':
        qry = text("""SELECT projectID, name FROM Projects WHERE projectID = :projectID""")
        project = engine.execute(qry, projectID=projectID).fetchone()
        qry = text("""SELECT filmID, title, fileNo, fileDate FROM Films WHERE projectID = :projectID""")
        films = engine.execute(qry, projectID=projectID).fetchall()
        return render_template('project.html', project=project, films=films)

@app.route('/projects/<int:projectID>/films/<int:filmID>',  methods = ['POST', 'GET'])
def film(projectID, filmID):
    if request.method == 'POST':
        lensID = None
        if request.form['lens'] != 'None':
            lensID = request.form['lens']

        qry = text("""INSERT INTO Exposures
            (filmID, exposureNumber, lensID, shutter, aperture)
            VALUES (:filmID, :exposureNumber, :lensID, :shutter, :aperture)""")
        result = engine.execute(qry,
            filmID = filmID,
            exposureNumber = request.form['exposureNumber'],
            lensID = lensID,
            shutter = request.form['shutter'],
            aperture = request.form['aperture'])

    # Reads
    qry = text("""SELECT filmID, Films.projectID, Projects.name AS project, brand,
        FilmTypes.name AS filmName, FilmTypes.iso AS filmISO,
        Films.iso AS shotISO, fileNo, fileDate, filmSize, title,
        development, Cameras.name AS camera, Cameras.cameraID AS cameraID, notes
        FROM Films
        JOIN Projects ON Projects.projectID = Films.projectID
        JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        LEFT JOIN Cameras ON Cameras.cameraID = Films.cameraID
        WHERE Films.projectID = :projectID AND filmID = :filmID""")
    film = engine.execute(qry, projectID=projectID, filmID=filmID).fetchone()

    # If we do not find a roll of film for the project, bail out so we
    # don't display any exposures. Preventing shenaigans with cross
    # project access.
    if not film:
        abort(404)

    qry = text("""SELECT filterID, name FROM Filters""")
    filters = engine.execute(qry).fetchall()

    qry = text("""SELECT CameraLenses.lensID, name FROM CameraLenses
        JOIN Lenses ON Lenses.lensID = CameraLenses.lensID
        WHERE CameraLenses.cameraID = :cameraID""")
    lenses = engine.execute(qry, cameraID=film.cameraID).fetchall()

    qry = text("""SELECT exposureNumber, shutter, aperture,
        Lenses.name AS lens, notes
        FROM Exposures
        LEFT JOIN Lenses ON Lenses.lensID = Exposures.lensID
        WHERE filmID = :filmID""")
    exposuresResult = engine.execute(qry, filmID=filmID).fetchall()
    exposures = result_to_dict(exposuresResult)
    for exposure in exposures:
        qry = text("""SELECT code FROM ExposureFilters
            JOIN Filters ON Filters.filterID = ExposureFilters.filterID
            WHERE filmID = :filmID AND exposureNumber = :exposureNumber""")
        filtersResult = engine.execute(qry, filmID=filmID,
            exposureNumber = exposure['exposureNumber']).fetchall()
        exposureFilters = result_to_dict(filtersResult)
        exposure['filters'] = exposureFilters
    return render_template('film.html',
        film=film, filters=filters, lenses=lenses, exposures=exposures)

@app.route('/filmtypes',  methods = ['GET'])
def filmtypes():
    if request.method == 'GET':
        qry = text("""SELECT filmTypeID, brand, name, iso, kind
                      FROM FilmTypes
                      JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID""")
        filmtypes = engine.execute(qry).fetchall()
        return render_template('filmtypes.html', filmtypes=filmtypes)


# Functions
def result_to_dict(result):
    return [dict(row) for row in result]
