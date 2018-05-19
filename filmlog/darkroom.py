from flask import request, render_template, redirect, url_for
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

from filmlog import app
from filmlog import database
from filmlog import functions

engine = database.engine

@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/prints',  methods = ['POST', 'GET'])
@login_required
def prints(binderID, projectID, filmID):
    connection = engine.connect()
    userID = current_user.get_id()
    film = functions.get_film_details(connection, binderID, projectID, filmID)

    return render_template('film/prints.html',
        binderID=binderID,
        film=film,
        view='prints')

@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/contactsheet',  methods = ['POST', 'GET'])
@login_required
def contactsheet(binderID, projectID, filmID):
    connection = engine.connect()
    userID = current_user.get_id()
    film = functions.get_film_details(connection, binderID, projectID, filmID)

    qry = text("""SELECT fileID, Papers.name AS paperName,
        PaperBrands.name AS paperBrand, PaperFilters.name AS paperFilterName,
        aperture, headHeight, exposureTime, notes
        FROM ContactSheets
        JOIN Papers ON Papers.paperID = ContactSheets.paperID
        JOIN PaperBrands ON PaperBrands.paperBrandID = Papers.paperBrandID
        JOIN PaperFilters ON PaperFilters.paperFilterID = ContactSheets.paperFilterID
        WHERE filmID = :filmID AND userID = :userID""")
    contactSheet =  connection.execute(qry,
        userID = userID,
        filmID=filmID).fetchone()
    return render_template('film/contactsheet.html',
        binderID=binderID,
        film=film,
        contactSheet = contactSheet,
        view='contactsheet')
