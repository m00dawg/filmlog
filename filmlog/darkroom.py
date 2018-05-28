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

def time_to_seconds(time):
    # If time is in MM:SS format, calculate the raw seconds
    # Otherwise just return the time as-is
    if time:
        if ':' not in time:
            return time
        m, s = time.split(':')
        return int(m) * 60 + int(s)
    return None

def seconds_to_time(seconds):
    return str(int(seconds / 60)) + ":" + str(int(seconds % 60))

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
        if request.form['button'] == 'deleteCS':
            qry = text("""SELECT fileID FROM ContactSheets
                WHERE filmID = :filmID AND userID = :userID""")
            result = connection.execute(qry,
                filmID = filmID,
                userID = userID).fetchone()
            fileID = result[0]
            qry = text("""DELETE FROM ContactSheets
                WHERE filmID = :filmID AND userID = :userID""")
            connection.execute(qry,
                filmID = filmID,
                userID = userID)
            files.delete_file(request, connection, transaction, fileID)
        else:
            nextFileID = functions.next_id(connection, 'fileID', 'Files')
            exposureTime = request.form['exposureTime']
            app.logger.debug('Exposure Time Before: %s', str(exposureTime))
            exposureTime = time_to_seconds(exposureTime)
            app.logger.debug('Exposure Time After: %s', str(exposureTime))
            if files.upload_file(request, connection, transaction, nextFileID):
                paperID = None
                paperFilterID = None
                notes = None
                if request.form['paperID'] != '':
                    paperID = request.form['paperID']
                if request.form['paperFilterID'] != '':
                    paperFilterID = request.form['paperFilterID']
                if request.form['notes'] != '':
                    paperFilterID = request.form['notes']

                qry = text("""REPLACE INTO ContactSheets (filmID, userID, fileID, paperID, paperFilterID, aperture, headHeight, exposureTime, notes)
                    VALUES (:filmID, :userID, :fileID, :paperID, :paperFilterID, :aperture, :headHeight, :exposureTime, :notes)""")
                connection.execute(qry,
                    filmID = filmID,
                    userID = userID,
                    fileID = nextFileID,
                    paperID = paperID,
                    paperFilterID = paperFilterID,
                    aperture = request.form['aperture'],
                    headHeight = request.form['headHeight'],
                    exposureTime = exposureTime,
                    notes = notes)
        transaction.commit()
        return redirect('/binders/' + str(binderID)
            + '/projects/' + str(projectID)
            + '/films/' + str(filmID)
            + '/contactsheet')

    film = functions.get_film_details(connection, binderID, projectID, filmID)

    # Get contact sheet info
    qry = text("""SELECT fileID, Papers.name AS paperName,
        PaperBrands.name AS paperBrand, PaperFilters.name AS paperFilterName,
        aperture, headHeight, notes,
        SECONDS_TO_DURATION(exposureTime) AS exposureTime
        FROM ContactSheets
        LEFT OUTER JOIN Papers ON Papers.paperID = ContactSheets.paperID
        LEFT OUTER JOIN PaperBrands ON PaperBrands.paperBrandID = Papers.paperBrandID
        LEFT OUTER JOIN PaperFilters ON PaperFilters.paperFilterID = ContactSheets.paperFilterID
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
