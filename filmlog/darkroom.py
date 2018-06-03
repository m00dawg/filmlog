from flask import request, render_template, redirect, url_for, flash, abort
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

# Forms
from flask_wtf import FlaskForm
from wtforms import Form, StringField, IntegerField, SelectField, RadioField, \
    DecimalField, TextAreaField, FileField, validators
from wtforms.validators import DataRequired, Optional, NumberRange, ValidationError
from flask_wtf.file import FileAllowed

from filmlog import app
from filmlog import database
from filmlog import functions
from filmlog import files

engine = database.engine

## Functions
def get_paper_filters(connection):
    qry = text("""SELECT paperFilterID, name FROM PaperFilters""")
    return connection.execute(qry).fetchall()

def get_papers(connection):
    # Get info for adding/updating contact sheet
    qry = text("""SELECT paperID,
        CONCAT(PaperBrands.name, " ", Papers.name) AS name
        FROM Papers
        JOIN PaperBrands ON PaperBrands.paperBrandID = Papers.paperBrandID""")
    return connection.execute(qry).fetchall()

def get_enlarger_lenses(connection):
    userID = current_user.get_id()
    qry = text("""SELECT enlargerLensID, name
        FROM EnlargerLenses
        WHERE userID = :userID""")
    return connection.execute(qry, userID = userID).fetchall()

def get_exposures(connection, filmID):
    userID = current_user.get_id()
    qry = text("""SELECT exposureNumber AS exposureNumber,
        exposureNumber AS subject
        FROM Exposures
        WHERE userID = :userID
        AND filmID = :filmID""")
    return connection.execute(qry,
        userID = userID, filmID = filmID).fetchall()

def time_to_seconds(time):
    # If time is in MM:SS format, calculate the raw seconds
    # Otherwise just return the time as-is
    if time:
        if ':' not in time:
            if int(time) > 0:
                return int(time)
        else:
            m, s = time.split(':')
            return int(m) * 60 + int(s)
    raise ValidationError('Time in wrong format, it should be MM:SS.')

def validate_exposure_time(form, field):
    try:
        time_to_seconds(field.data)
    except Exception:
        raise ValidationError('Time in wrong format, it should be in MM:SS or in seconds.')

def seconds_to_time(seconds):
    return str(int(seconds / 60)) + ":" + str(int(seconds % 60))

def optional_choices(name, choices):
    new_choices = [(0, name)]
    for row in choices:
        new_choices.append(row)
    return new_choices

def zero_to_none(value):
    if value == 0:
        return None
    return value

## Classes
# Forms
class PrintForm(FlaskForm):
    exposureNumber = SelectField('Exposure #',
        validators=[Optional()],
        coerce=int)
    paperID = SelectField('Paper',
        validators=[Optional()],
        coerce=int)
    paperFilterID = SelectField('Filters',
        validators=[Optional()],
        coerce=int)
    printType = SelectField('Type',
        validators=[DataRequired()],
        choices=[('Enlargement', 'Enlargement'), ('Contact', 'Contact')])
    size = SelectField('Size',
        validators=[DataRequired()],
        choices=[('4x5', '4x5'), ('5x7', '5x7'), ('8x10', '8x10')])
    enlargerLensID = SelectField('Enlarger Lens',
        validators=[Optional()],
        coerce=int)
    aperture = DecimalField('Aperture', places=1,
        validators=[Optional()])
    headHeight = IntegerField('Head Height',
        validators=[NumberRange(min=0,max=255),
                    Optional()])
    exposureTime = StringField('Exposure Time',
        validators=[DataRequired(), validate_exposure_time])
    notes = TextAreaField('Notes',
        validators=[Optional()])
    file = FileField('File (JPG)',
        validators=[Optional(), FileAllowed(['jpg'], 'JPEGs Only')])

    def __init__(self, connection, filmID):
        super(PrintForm, self).__init__()
        self.connection = connection
        self.paperID.choices = optional_choices("None", get_papers(connection))
        self.paperFilterID.choices = optional_choices("None", get_paper_filters(connection))
        self.enlargerLensID.choices = optional_choices("None", get_enlarger_lenses(connection))
        self.exposureNumber.choices = get_exposures(connection, filmID)

class ContactSheetForm(FlaskForm):
    paperID = SelectField('Paper',
        validators=[Optional()],
        coerce=int)
    paperFilterID = SelectField('Filters',
        validators=[Optional()],
        coerce=int)
    enlargerLensID = SelectField('Enlarger Lens',
        validators=[Optional()],
        coerce=int)
    aperture = DecimalField('Aperture', places=1,
        validators=[Optional()])
    headHeight = IntegerField('Head Height',
        validators=[NumberRange(min=0,max=255),
                    Optional()])
    exposureTime = StringField('Exposure Time',
        validators=[DataRequired(), validate_exposure_time])
    notes = TextAreaField('Notes',
        validators=[Optional()])
    file = FileField('File (JPG)',
        validators=[Optional(), FileAllowed(['jpg'], 'JPEGs Only')])

    def __init__(self, connection):
        super(ContactSheetForm, self).__init__()
        self.connection = connection
        self.paperID.choices = optional_choices("None", get_papers(connection))
        self.paperFilterID.choices = optional_choices("None", get_paper_filters(connection))
        self.enlargerLensID.choices = optional_choices("None", get_enlarger_lenses(connection))

@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/prints',  methods = ['POST', 'GET'])
@login_required
def prints(binderID, projectID, filmID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = PrintForm(connection, filmID)

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
            if fileID:
                files.delete_file(request, connection, transaction, fileID)

        if request.form['button'] == 'addPrint':
            if form.validate_on_submit():
                nextPrintID = functions.next_id(connection, 'printID', 'Prints')
                # If user included a file, let's upload it. Otherwise skip it.
                if form.file.data:
                    nextFileID = functions.next_id(connection, 'fileID', 'Files')
                    files.upload_file(request, connection, transaction, nextFileID)
                else:
                    nextFileID = None

                qry = text("""INSERT INTO Prints
                    (printID, filmID, exposureNumber, userID, paperID, paperFilterID,
                    enlargerLensID, fileID, aperture, headHeight, exposureTime, printType, size, notes)
                    VALUES (:printID, :filmID, :exposureNumber, :userID, :paperID,
                    :paperFilterID, :enlargerLensID, :fileID, :aperture, :headHeight, :exposureTime,
                    :printType, :size, :notes)""")
                connection.execute(qry,
                    printID = nextPrintID,
                    filmID = filmID,
                    userID = userID,
                    fileID = nextFileID,
                    exposureNumber = form.exposureNumber.data,
                    paperID = zero_to_none(form.paperID.data),
                    paperFilterID = zero_to_none(form.paperFilterID.data),
                    enlargerLensID = zero_to_none(form.enlargerLensID.data),
                    aperture = form.aperture.data,
                    headHeight = form.headHeight.data,
                    exposureTime = time_to_seconds(form.exposureTime.data),
                    printType = form.printType.data,
                    size = form.size.data,
                    notes = form.notes.data)
    film = functions.get_film_details(connection, binderID, projectID, filmID)

    qry = text("""SELECT printID, exposureNumber, Papers.name AS paperName,
        PaperBrands.name AS paperBrand, PaperFilters.name AS paperFilterName,
        printType, size, aperture, headHeight, notes, fileID,
        EnlargerLenses.name AS lens,
        SECONDS_TO_DURATION(exposureTime) AS exposureTime
        FROM Prints
        LEFT OUTER JOIN Papers ON Papers.paperID = Prints.paperID
        LEFT OUTER JOIN PaperBrands ON PaperBrands.paperBrandID = Papers.paperBrandID
        LEFT OUTER JOIN PaperFilters ON PaperFilters.paperFilterID = Prints.paperFilterID
        LEFT OUTER JOIN EnlargerLenses ON EnlargerLenses.enlargerLensID = Prints.enlargerLensID
            AND EnlargerLenses.userID = Prints.userID
        WHERE filmID = :filmID AND Prints.userID = :userID""")
    prints = connection.execute(qry,
        userID = userID,
        filmID = filmID)

    transaction.commit()
    return render_template('darkroom/prints.html',
        form = form,
        binderID=binderID,
        film=film,
        prints = prints,
        view='prints')

@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/contactsheet',  methods = ['POST', 'GET'])
@login_required
def contactsheet(binderID, projectID, filmID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = ContactSheetForm(connection)

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
            if fileID:
                files.delete_file(request, connection, transaction, fileID)
        elif request.form['button'] == 'updateCS' and form.validate_on_submit():
            # If user included a file, let's upload it. Otherwise skip it.
            if 'file' in request.files:
                nextFileID = functions.next_id(connection, 'fileID', 'Files')
                files.upload_file(request, connection, transaction, nextFileID)
            else:
                nextFileID = None

            qry = text("""REPLACE INTO ContactSheets (filmID, userID, fileID, paperID, paperFilterID, enlargerLensID, aperture, headHeight, exposureTime, notes)
                VALUES (:filmID, :userID, :fileID, :paperID, :paperFilterID, :enlargerLensID, :aperture, :headHeight, :exposureTime, :notes)""")
            connection.execute(qry,
                filmID = filmID,
                userID = userID,
                fileID = nextFileID,
                paperID = zero_to_none(form.paperID.data),
                paperFilterID = zero_to_none(form.paperFilterID.data),
                enlargerLensID = zero_to_none(form.enlargerLensID.data),
                aperture = form.aperture.data,
                headHeight = form.headHeight.data,
                exposureTime = time_to_seconds(form.exposureTime.data),
                notes = form.notes.data)

    film = functions.get_film_details(connection, binderID, projectID, filmID)

    # Get contact sheet info
    qry = text("""SELECT fileID, Papers.name AS paperName,
        PaperBrands.name AS paperBrand, PaperFilters.name AS paperFilterName,
        EnlargerLenses.name AS lens, aperture, headHeight, notes,
        SECONDS_TO_DURATION(exposureTime) AS exposureTime
        FROM ContactSheets
        LEFT OUTER JOIN Papers ON Papers.paperID = ContactSheets.paperID
        LEFT OUTER JOIN PaperBrands ON PaperBrands.paperBrandID = Papers.paperBrandID
        LEFT OUTER JOIN PaperFilters ON PaperFilters.paperFilterID = ContactSheets.paperFilterID
        LEFT OUTER JOIN EnlargerLenses ON EnlargerLenses.enlargerLensID = ContactSheets.enlargerLensID
            AND EnlargerLenses.userID = ContactSheets.userID
        WHERE filmID = :filmID AND ContactSheets.userID = :userID""")
    contactSheet =  connection.execute(qry,
        userID = userID,
        binderID = binderID,
        filmID=filmID).fetchone()

    filters = get_paper_filters(connection)
    papers = get_papers(connection)
    enlargerLenses = get_enlarger_lenses(connection)

    transaction.commit()
    return render_template('darkroom/contactsheet.html',
        binderID=binderID,
        papers=papers,
        filters=filters,
        film=film,
        enlargerLenses=enlargerLenses,
        contactSheet = contactSheet,
        form=form,
        view='contactsheet')
