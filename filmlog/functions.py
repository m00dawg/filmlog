from filmlog import app, abort
from sqlalchemy.sql import text
from flask_login import current_user

# Functions
def result_to_dict(result_set):
    return [dict(row) for row in result_set]

# This allows for SQL injection if yuo're not careful!
def next_id(connection, field, table):
    qry = text("""SELECT MAX(""" + field + """) AS currentID FROM """ + table + """ WHERE userID = :userID""")
    result = connection.execute(qry,
        userID = int(current_user.get_id())).fetchone()
    app.logger.info('Current ID: %s', result.currentID)
    if result.currentID is not None:
        return int(result.currentID) + 1
    else:
        return 1

def get_film_details(connection, binderID, projectID, filmID):
    userID = current_user.get_id()

    qry = text("""SELECT filmID, Films.projectID, Projects.name AS project, brand,
        FilmTypes.name AS filmName, FilmTypes.iso AS filmISO,
        Films.iso AS shotISO, fileNo, fileDate, filmSize, title,
        FilmTypes.filmTypeID AS filmTypeID, loaded, unloaded, developed, development,
        Cameras.name AS camera,
        Cameras.cameraID AS cameraID, notes
        FROM Films
        JOIN Projects ON Projects.projectID = Films.projectID
        JOIN Binders ON Binders.binderID = Projects.binderID
        JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        LEFT JOIN Cameras ON Cameras.cameraID = Films.cameraID
        WHERE Films.projectID = :projectID
        AND filmID = :filmID
        AND Projects.binderID = :binderID
        AND Binders.userID = :userID""")

    film = connection.execute(qry,
        userID = userID,
        binderID = binderID,
        projectID=projectID,
        filmID=filmID).fetchone()

    if not film:
        abort(404)

    return film

def optional_choices(name, choices):
    new_choices = [(0, name)]
    for row in choices:
        new_choices.append(row)
    return new_choices


def zero_to_none(value):
    if value == 0:
        return None
    return value
