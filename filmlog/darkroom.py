from flask import request, render_template, redirect, url_for
from sqlalchemy.sql import select, text, func
import os, re

from filmlog import app
from filmlog import database
from filmlog import functions

engine = database.engine

@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/prints',  methods = ['POST', 'GET'])
def prints(binderID, projectID, filmID):

    # Stolen from film route - needs to be a function?
    # Reads
    qry = text("""SELECT filmID, Films.projectID, Projects.name AS project, brand,
        FilmTypes.name AS filmName, FilmTypes.iso AS filmISO,
        Films.iso AS shotISO, fileNo, fileDate, filmSize, title,
        loaded, unloaded, developed, development, Cameras.name AS camera,
        Cameras.cameraID AS cameraID, notes
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

    return render_template('film/prints.html',
        binderID=binderID,
        film=film,
        view='prints')
