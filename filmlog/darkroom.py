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

def get_papers(connection):
    # Get info for adding/updating contact sheet
    qry = text("""SELECT paperID, PaperBrands.name AS brandName, Papers.name AS paperName
        FROM Papers
        JOIN PaperBrands ON PaperBrands.paperBrandID = Papers.paperBrandID""")
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
    transaction = connection.begin()
    userID = current_user.get_id()

    if request.method == 'POST':
        if request.form['button'] == 'deletePrint':
            printID = request.form['printID']
            qry = text("""SELECT fileID FROM Prints
                WHERE printID = :printID AND userID = :userID""")
            result = connection.execute(qry,
                printID = printID,
                userID = userID).fetchone()
            fileID = result[0]
            qry = text("""DELETE FROM Prints
                WHERE printID = :printID
                AND userID = :userID""")
            connection.execute(qry,
                printID = printID,
                userID = userID)
            files.delete_file(request, connection, transaction, fileID)

        if request.form['button'] == 'addPrint':
            paperID = None
            paperFilterID = None
            headHeight = None
            aperture = None
            notes = None
            nextPrintID = functions.next_id(connection, 'printID', 'Prints')
            exposureTime = time_to_seconds(request.form['exposureTime'])

            # If user included a file, let's upload it. Otherwise skip it.
            if 'file' in request.files:
                nextFileID = functions.next_id(connection, 'fileID', 'Files')
                files.upload_file(request, connection, transaction, nextFileID)
            else:
                nextFileID = None

            if request.form['paperID'] != '':
                paperID = request.form['paperID']
            if request.form['paperFilterID'] != '':
                paperFilterID = request.form['paperFilterID']
            if request.form['headHeight'] != '':
                headHeight = request.form['headHeight']
            if request.form['aperture'] != '':
                aperture = request.form['aperture']
            if request.form['notes'] != '':
                notes = request.form['notes']

            qry = text("""INSERT INTO Prints
                (printID, filmID, exposureNumber, userID, paperID, paperFilterID,
                fileID, aperture, headHeight, exposureTime, printType, size, notes)
                VALUES (:printID, :filmID, :exposureNumber, :userID, :paperID,
                :paperFilterID, :fileID, :aperture, :headHeight, :exposureTime,
                :printType, :size, :notes)""")
            connection.execute(qry,
                printID = nextPrintID,
                filmID = filmID,
                exposureNumber = request.form['exposureNumber'],
                userID = userID,
                paperID = paperID,
                paperFilterID = paperFilterID,
                fileID = nextFileID,
                aperture = aperture,
                headHeight = headHeight,
                exposureTime = exposureTime,
                printType = request.form['printType'],
                size = request.form['size'],
                notes = request.form['notes'])

    film = functions.get_film_details(connection, binderID, projectID, filmID)
    papers = get_papers(connection)
    filters = get_paper_filters(connection)

    qry = text("""SELECT printID, exposureNumber, Papers.name AS paperName,
        PaperBrands.name AS paperBrand, PaperFilters.name AS paperFilterName,
        printType, size, aperture, headHeight, notes, fileID,
        SECONDS_TO_DURATION(exposureTime) AS exposureTime
        FROM Prints
        LEFT OUTER JOIN Papers ON Papers.paperID = Prints.paperID
        LEFT OUTER JOIN PaperBrands ON PaperBrands.paperBrandID = Papers.paperBrandID
        LEFT OUTER JOIN PaperFilters ON PaperFilters.paperFilterID = Prints.paperFilterID
        WHERE filmID = :filmID AND userID = :userID""")
    prints = connection.execute(qry,
        userID = userID,
        filmID = filmID)

    transaction.commit()
    return render_template('darkroom/prints.html',
        binderID=binderID,
        film=film,
        papers=papers,
        filters=filters,
        prints = prints,
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
            exposureTime = request.form['exposureTime']
            app.logger.debug('Exposure Time Before: %s', str(exposureTime))
            exposureTime = time_to_seconds(exposureTime)
            app.logger.debug('Exposure Time After: %s', str(exposureTime))

            # If user included a file, let's upload it. Otherwise skip it.
            if 'file' in request.files:
                nextFileID = functions.next_id(connection, 'fileID', 'Files')
                files.upload_file(request, connection, transaction, nextFileID)
            else:
                nextFileID = None

            paperID = None
            paperFilterID = None
            headHeight = None
            notes = None
            if request.form['paperID'] != '':
                paperID = request.form['paperID']
            if request.form['paperFilterID'] != '':
                paperFilterID = request.form['paperFilterID']
            if request.form['headHeight'] != '':
                headHeight = request.form['headHeight']
            if request.form['notes'] != '':
                notes = request.form['notes']

            qry = text("""REPLACE INTO ContactSheets (filmID, userID, fileID, paperID, paperFilterID, aperture, headHeight, exposureTime, notes)
                VALUES (:filmID, :userID, :fileID, :paperID, :paperFilterID, :aperture, :headHeight, :exposureTime, :notes)""")
            connection.execute(qry,
                filmID = filmID,
                userID = userID,
                fileID = nextFileID,
                paperID = paperID,
                paperFilterID = paperFilterID,
                aperture = request.form['aperture'],
                headHeight = headHeight,
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

    filters = get_paper_filters(connection)
    papers = get_papers(connection)

    transaction.commit()
    return render_template('darkroom/contactsheet.html',
        binderID=binderID,
        papers=papers,
        filters=filters,
        film=film,
        contactSheet = contactSheet,
        view='contactsheet')
