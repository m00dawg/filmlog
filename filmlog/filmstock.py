from flask import request, render_template, redirect, url_for, abort
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user

# Forms
from flask_wtf import FlaskForm
from wtforms import Form, StringField, DateField, SelectField, IntegerField, \
    TextAreaField, DecimalField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from wtforms import widgets

from filmlog import app
from filmlog import database
from filmlog.functions import get_film_types

engine = database.engine

class FilmStockForm(FlaskForm):
    filmTypeID = SelectField('Film',
            validators=[DataRequired()],
            coerce=int)
    filmSize = SelectField('Film Size',
        validators=[Optional()],
        choices=[('35mm 24', '35mm 24'),
                 ('35mm 36', '35mm 36'),
                 ('35mm Hand Rolled', '35mm Hand Rolled'),
                 ('35mm 100'' Bulk Roll', '35mm 100'' Bulk Roll'),
                 ('120', '120'),
                 ('220', '220'),
                 ('4x5', '4x5'),
                 ('8x10', '8x10')])
    qty = IntegerField('Qty',
        validators=[NumberRange(min=1,max=65535),
                    DataRequired()])

    def populate_select_fields(self, connection):
        self.connection = connection
        self.filmTypeID.choices = get_film_types(connection)

@app.route('/filmstock',  methods = ['GET', 'POST'])
@login_required
def filmstock():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    form = FilmStockForm()
    form.populate_select_fields(connection)

    if request.method == 'POST':
        if request.form.get('button') == 'increment':
            if request.form.get('filmTypeID') != '' and request.form.get('filmSize') != '':
                qry = text("""UPDATE FilmStock SET qty = qty + 1
                    WHERE filmTypeID = :filmTypeID
                    AND filmSize = :filmSize
                    AND userID = :userID""")
                connection.execute(qry,
                    filmTypeID=request.form.get('filmTypeID'),
                    filmSize=request.form.get('filmSize'),
                    userID = userID)
        if request.form.get('button') == 'decrement':
            if request.form.get('filmTypeID') != '' and request.form.get('filmSize') != '':
                qry = text("""SELECT qty FROM FilmStock
                    WHERE filmTypeID = :filmTypeID
                    AND filmSize = :filmSize
                    AND userID = :userID""")
                result = connection.execute(qry,
                    filmTypeID=request.form.get('filmTypeID'),
                    filmSize=request.form.get('filmSize'),
                    userID = userID).fetchone()
                if result.qty == 1:
                    qry = text(""" DELETE FROM FilmStock
                        WHERE filmTypeID = :filmTypeID
                        AND filmSize = :filmSize
                        AND userID = :userID""")
                    connection.execute(qry,
                        filmTypeID=request.form.get('filmTypeID'),
                        filmSize=request.form.get('filmSize'),
                        userID = userID)
                else:
                    qry = text("""UPDATE FilmStock SET qty = qty - 1
                        WHERE filmTypeID = :filmTypeID
                        AND filmSize = :filmSize
                        AND userID = :userID""")
                    connection.execute(qry,
                        filmTypeID=request.form.get('filmTypeID'),
                        filmSize=request.form.get('filmSize'),
                        userID = userID)
        if request.form.get('button') == 'add':
            qty = request.form.get('qty')
            if request.form.get('filmTypeID') != '':
                if qty != '':
                    qty = int(qty)
                    if qty > 0:
                        qry = text("""REPLACE INTO FilmStock
                            (filmTypeID, filmSize, userID, qty)
                            VALUES (:filmTypeID, :filmSize, :userID, :qty)""")
                        result = connection.execute(qry,
                            filmTypeID=form.filmTypeID.data,
                            filmSize=form.filmSize.data,
                            qty=form.qty.data,
                            userID = userID)
    qry = text("""SELECT FilmStock.filmTypeID AS filmTypeID, filmSize, qty,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmStock
        JOIN FilmTypes ON FilmTypes.filmTypeID = FilmStock.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE filmSize IN ("35mm 24", "35mm 36", "35mm Hand Rolled", "35mm 100' Bulk Roll")
        AND userID = :userID
        ORDER BY filmSize, brand, type, iso""")
    stock_35mm = connection.execute(qry, userID = userID).fetchall()

    qry = text("""SELECT FilmStock.filmTypeID AS filmTypeID, filmSize, qty,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmStock
        JOIN FilmTypes ON FilmTypes.filmTypeID = FilmStock.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE filmSize IN ('120', '220')
        AND userID = :userID
        ORDER BY filmSize, brand, type, iso""")
    stock_mf = connection.execute(qry, userID = userID).fetchall()

    qry = text("""SELECT FilmStock.filmTypeID AS filmTypeID, filmSize, qty,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmStock
        JOIN FilmTypes ON FilmTypes.filmTypeID = FilmStock.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE filmSize IN ('4x5', '8x10')
        AND userID = :userID
        ORDER BY filmSize, brand, type, iso""")
    stock_sheets = connection.execute(qry, userID = userID).fetchall()

    qry = text("""SELECT FilmTypes.filmTypeID AS filmTypeID,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmTypes
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID""")
    films = connection.execute(qry).fetchall()

    transaction.commit()
    return render_template('filmstock.html',
                form=form,
                stock_35mm=stock_35mm,
                stock_mf=stock_mf,
                stock_sheets=stock_sheets,
                films=films)

@app.route('/filmtypes',  methods = ['GET'])
@login_required
def filmtypes():
    connection = engine.connect()
    qry = text("""SELECT filmTypeID, brand, name, iso, kind
        FROM FilmTypes
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        ORDER BY brand, name, iso, kind""")
    filmtypes = connection.execute(qry).fetchall()
    return render_template('filmtypes.html', filmtypes=filmtypes)
