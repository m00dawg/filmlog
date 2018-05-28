from flask import request, render_template, redirect, url_for, flash, abort
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

from filmlog import app
from filmlog import database
from filmlog import functions
from filmlog import files

engine = database.engine

def get_paper_filters(connection):
    qry = text("""SELECT paperFilterID, name FROM PaperFilters""")
    return connection.execute(qry).fetchall()

@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/prints',  methods = ['POST', 'GET'])
@login_required
def prints(binderID, projectID, filmID):
    connection = engine.connect()
    userID = current_user.get_id()
    film = functions.get_film_details(connection, binderID, projectID, filmID)

    return render_template('darkroom/prints.html',
        binderID=binderID,
        film=film,
        view='prints')

@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/contactsheet',  methods = ['POST', 'GET'])
@login_required
def contactsheet(binderID, projectID, filmID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    # Upload a new contact sheet
    if request.method == 'POST':
        nextFileID = functions.next_id(connection, 'fileID', 'Files')
        exposureTime = request.form['exposureTime']
        if(exposureTime.count(':') == 1):
            exposureTime = "00:" + exposureTime
        print exposureTime
        if files.upload_file(request, connection, transaction, nextFileID):
            qry = text("""REPLACE INTO ContactSheets (filmID, userID, fileID, paperID, paperFilterID, aperture, headHeight, exposureTime, notes)
                VALUES (:filmID, :userID, :fileID, :paperID, :paperFilterID, :aperture, :headHeight, :exposureTime, :notes)""")
            connection.execute(qry,
                filmID = filmID,
                userID = userID,
                fileID = nextFileID,
                paperID = request.form['paper'],
                paperFilterID = request.form['filter'],
                aperture = request.form['aperture'],
                headHeight = request.form['headHeight'],
                exposureTime = exposureTime,
                notes = request.form['notes'])
            transaction.commit()
            return redirect('/binders/' + str(binderID)
                + '/projects/' + str(projectID)
                + '/films/' + str(filmID)
                + '/contactsheet')

    film = functions.get_film_details(connection, binderID, projectID, filmID)

    # Get contact sheet info
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
        binderID = binderID,
        filmID=filmID).fetchone()

    # Get info for adding/updating contact sheet
    qry = text("""SELECT paperID, PaperBrands.name AS brandName, Papers.name AS paperName
        FROM Papers
        JOIN PaperBrands ON PaperBrands.paperBrandID = Papers.paperBrandID""")

    papers = connection.execute(qry).fetchall()
    filters = get_paper_filters(connection)

    transaction.commit()
    return render_template('darkroom/contactsheet.html',
        binderID=binderID,
        papers=papers,
        filters=filters,
        film=film,
        contactSheet = contactSheet,
        view='contactsheet')
