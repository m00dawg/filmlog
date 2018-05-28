from flask import request, render_template, redirect, url_for, flash, abort
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

from filmlog import app
from filmlog import database
from filmlog import functions
from filmlog import files

engine = database.engine

@app.route('/stats/', methods = ['GET'])
@login_required
def stats():
    connection = engine.connect()
    userID = current_user.get_id()

    qry = text("""SELECT Cameras.name, COUNT(Films.cameraID) AS count
        FROM Cameras
        JOIN Films ON Films.cameraID = Cameras.cameraID
        AND Films.userID = Cameras.userID
        WHERE Cameras.userID=:userID
        GROUP BY Films.cameraID
        ORDER BY COUNT(Films.cameraID) DESC""")
    cameras =  connection.execute(qry, userID = userID)

    qry = text("""SELECT
        FilmBrands.brand AS brand, FilmTypes.name AS type, FilmTypes.iso AS iso,
        COUNT(Films.filmTypeID) AS count
        FROM Films
        JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        AND userID = :userID
        GROUP BY Films.filmTypeID
        ORDER BY COUNT(Films.filmTypeID) DESC""")
    favoriteRolls =  connection.execute(qry, userID = userID)

    qry = text("""SELECT
        FilmBrands.brand AS brand, FilmTypes.name AS type, FilmTypes.iso AS iso,
        COUNT(Exposures.filmTypeID) AS count
        FROM Exposures
        JOIN FilmTypes ON FilmTypes.filmTypeID = Exposures.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        AND userID = :userID
        GROUP BY Exposures.filmTypeID
        ORDER BY COUNT(Exposures.filmTypeID) DESC""")
    favoriteSheets =  connection.execute(qry, userID = userID)

    return render_template('/stats.html',
        cameras=cameras,
        favoriteRolls = favoriteRolls,
        favoriteSheets = favoriteSheets)
