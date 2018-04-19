from flask import request, render_template, redirect, url_for, abort
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user

from filmlog import app
from filmlog import database
from filmlog import functions

engine = database.engine

@app.route('/filmstock',  methods = ['GET', 'POST'])
@login_required
def filmstock():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    if request.method == 'POST':
        if request.form.get('button') == 'increment':
            if request.form.get('filmTypeID') != '' and request.form.get('filmSize') != '':
                qry = text("""UPDATE FilmStock SET qty = qty + 1
                    WHERE filmTypeID = :filmTypeID
                    AND filmSize = :filmSize
                    AND userID = :userID""")
                result = engine.execute(qry,
                    filmTypeID=request.form.get('filmTypeID'),
                    filmSize=request.form.get('filmSize'),
                    userID = userID)
        if request.form.get('button') == 'decrement':
            if request.form.get('filmTypeID') != '' and request.form.get('filmSize') != '':
                qry = text("""SELECT qty FROM FilmStock
                    WHERE filmTypeID = :filmTypeID
                    AND filmSize = :filmSize
                    AND userID = :userID""")
                result = engine.execute(qry,
                    filmTypeID=request.form.get('filmTypeID'),
                    filmSize=request.form.get('filmSize'),
                    userID = userID).fetchone()
                if result.qty == 1:
                    qry = text(""" DELETE FROM FilmStock
                        WHERE filmTypeID = :filmTypeID
                        AND filmSize = :filmSize
                        AND userID = :userID""")
                    engine.execute(qry,
                        filmTypeID=request.form.get('filmTypeID'),
                        filmSize=request.form.get('filmSize'),
                        userID = userID)
                else:
                    qry = text("""UPDATE FilmStock SET qty = qty - 1
                        WHERE filmTypeID = :filmTypeID
                        AND filmSize = :filmSize
                        AND userID = :userID""")
                    result = engine.execute(qry,
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
                        result = engine.execute(qry,
                            filmTypeID=request.form.get('filmTypeID'),
                            filmSize=request.form.get('filmSize'),
                            userID = userID,
                            qty=request.form.get('qty'))
    qry = text("""SELECT FilmStock.filmTypeID AS filmTypeID, filmSize, qty,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmStock
        JOIN FilmTypes ON FilmTypes.filmTypeID = FilmStock.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE filmSize IN ("35mm 24", "35mm 36", "35mm Hand Roll", "35mm 100' Bulk Roll")
        AND userID = :userID
        ORDER BY filmSize, brand, type, iso""")
    stock_35mm = engine.execute(qry, userID = userID).fetchall()

    qry = text("""SELECT FilmStock.filmTypeID AS filmTypeID, filmSize, qty,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmStock
        JOIN FilmTypes ON FilmTypes.filmTypeID = FilmStock.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE filmSize IN ('120', '220')
        AND userID = :userID
        ORDER BY filmSize, brand, type, iso""")
    stock_mf = engine.execute(qry, userID = userID).fetchall()

    qry = text("""SELECT FilmStock.filmTypeID AS filmTypeID, filmSize, qty,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmStock
        JOIN FilmTypes ON FilmTypes.filmTypeID = FilmStock.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE filmSize IN ('4x5', '8x10')
        AND userID = :userID
        ORDER BY filmSize, brand, type, iso""")
    stock_sheets = engine.execute(qry, userID = userID).fetchall()

    qry = text("""SELECT FilmTypes.filmTypeID AS filmTypeID,
        FilmBrands.brand AS brand, FilmTypes.name AS type, iso
        FROM FilmTypes
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID""")
    films = engine.execute(qry).fetchall()
    
    transaction.commit()
    return render_template('filmstock.html',
                stock_35mm=stock_35mm,
                stock_mf=stock_mf,
                stock_sheets=stock_sheets,
                films=films)
