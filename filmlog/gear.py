from flask import request, render_template, redirect, url_for, Response, session, abort, send_from_directory
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

from filmlog import app
from filmlog import database
from filmlog import functions

engine = database.engine

# Forms
from flask_wtf import FlaskForm
from wtforms import Form, StringField, DateField, SelectField, IntegerField, \
    TextAreaField, DecimalField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from wtforms import widgets

class CameraForm(FlaskForm):
    name = StringField('Name',
        validators=[DataRequired(), Length(min=1, max=64)])
    filmSize = SelectField('Film Size',
        validators=[DataRequired()],
        choices=[
            ('35mm', '35mm'),
            ('120', '120'),
            ('220', '220'),
            ('4x5', '4x5'),
            ('8x10', '8x10')])

@app.route('/gear',  methods = ['GET', 'POST'])
@login_required
def gear():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    camera_form = CameraForm()

    if request.method == 'POST':
        app.logger.debug('POST')
        if request.form['button'] == 'addCamera':
            app.logger.debug('Add Camera')
            nextCameraID = next_id(connection, 'cameraID', 'Cameras')
            qry = text("""INSERT INTO Cameras
                (cameraID, userID, name, filmSize) VALUES (:cameraID, :userID, :name, :filmSize)""")
            connection.execute(qry,
                cameraID = nextCameraID,
                userID = int(current_user.get_id()),
                name = request.form['name'],
                filmSize = request.form['filmSize'],
                )
        if request.form['button'] == 'addFilter':
            nextFilterID = next_id(connection, 'filterID', 'Filters')
            qry = text("""INSERT INTO Filters
                (userID, filterID, name, code, factor, ev)
                VALUES (:userID, :filterID, :name, :code, :factor, :ev)""")
            connection.execute(qry,
                userID = userID,
                filterID = nextFilterID,
                name = request.form['name'],
                code = request.form['code'],
                factor = request.form['factor'],
                ev = request.form['ev'])

    qry = text("""SELECT cameraID, name, filmSize
        FROM Cameras
        WHERE userID = :userID""")
    cameras = connection.execute(qry, userID = userID).fetchall()

    qry = text("""SELECT filterID, name, code, factor, ev
                  FROM Filters
                  WHERE userID = :userID""")
    filters = connection.execute(qry, userID = current_user.get_id()).fetchall()
    transaction.commit()
    return render_template('gear.html',
        camera_form = camera_form,
        cameras=cameras, filters=filters)
