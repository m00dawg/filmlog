from flask import request, render_template, redirect, url_for, Response, session, abort, send_from_directory
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

from filmlog import app
from filmlog import database
from filmlog.functions import next_id, result_to_dict, get_film_details
from filmlog import users
from filmlog import filmstock
from filmlog import darkroom
from filmlog import files
from filmlog import stats

engine = database.engine


def get_film_types(connection):
    qry = text("""SELECT filmTypeID, brand, name, iso FROM FilmTypes
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        ORDER BY brand, name""")
    return connection.execute(qry).fetchall()

@app.route('/',  methods = ['GET'])
def index():
    userID = current_user.get_id()
    if userID:
        return render_template('overview.html')
    else:
        return render_template('public/index.html')

# Binder List
@app.route('/binders',  methods = ['POST', 'GET'])
@login_required
def binders():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    if request.method == 'POST':
        nextBinderID = next_id(connection, 'binderID', 'Binders')
        qry = text("""INSERT INTO Binders
            (binderID, userID, name) VALUES (:binderID, :userID, :name)""")
        result = connection.execute(qry,
            binderID = nextBinderID,
            userID = userID,
            name = request.form['name'])
    qry = text("""SELECT binderID, name, projectCount, createdOn
        FROM Binders WHERE userID = :userID""")
    binders = connection.execute(qry, userID = userID).fetchall()
    transaction.commit()
    return render_template('binders.html', binders=binders)

# Project List
@app.route('/binders/<int:binderID>/projects',  methods = ['POST', 'GET'])
@login_required
def projects(binderID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    # Get current binder (and check to make sure a user isn't trying to
    # access someone else's binder)
    qry = text("""SELECT binderID, name FROM Binders
        WHERE binderID = :binderID AND userID = :userID ORDER BY createdOn""")
    binder = connection.execute(qry,
        binderID=binderID,
        userID=userID).fetchone()
    if binder is None:
        abort(404)

    if request.method == 'POST':
        nextProjectID = next_id(connection, 'projectID', 'Projects')
        qry = text("""INSERT INTO Projects
            (projectID, binderID, userID, name)
            VALUES (:projectID, :binderID, :userID, :name)""")
        result = connection.execute(qry,
            projectID = nextProjectID,
            binderID = binderID,
            userID = userID,
            name = request.form['name'])

    qry = text("""SELECT projectID, name, filmCount, createdOn FROM Projects
        WHERE binderID = :binderID
        AND userID = :userID
        ORDER BY createdOn""")
    projects = connection.execute(qry, binderID=binderID, userID = userID).fetchall()
    transaction.commit()
    return render_template('projects.html', binder=binder, binderID=binderID, projects=projects)

# Project Films List
@app.route('/binders/<int:binderID>/projects/<int:projectID>',  methods = ['POST', 'GET'])
@login_required
def project(binderID, projectID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    qry = text("""SELECT projectID, Projects.name AS name
        FROM Projects
        JOIN Binders ON Binders.binderID = Projects.binderID
            AND Binders.userID = Projects.userID
        WHERE projectID = :projectID
        AND Projects.binderID = :binderID
        AND Projects.userID = :userID
        ORDER BY Projects.createdOn""")
    project = connection.execute(qry,
        projectID = projectID,
        binderID = binderID,
        userID = userID).fetchone()
    if project is None:
        abort(404)

    if request.method == 'POST':
        title = None
        fileNo = None
        fileDate = None
        loaded = None
        unloaded = None
        developed = None

        if request.form['title'] != '':
            title = request.form['title']
        if request.form['fileNo'] != '':
            fileNo = request.form['fileNo']
        if request.form['fileDate'] != '':
            fileDate = request.form['fileDate']
        if request.form['loaded'] != '':
            loaded = request.form['loaded']
        if request.form['unloaded'] != '':
            unloaded = request.form['unloaded']
        if request.form['developed'] != '':
            developed = request.form['developed']


        nextFilmID = next_id(connection, 'filmID', 'Films')

        qry = text("""INSERT INTO Films
            (userID, filmID, projectID, cameraID, title, fileNo, fileDate, filmTypeID, iso,
             loaded, unloaded, developed, development, notes)
            VALUES (:userID, :filmID, :projectID, :cameraID, :title, UPPER(:fileNo),
                    :fileDate, :filmTypeID, :iso, :loaded, :unloaded,
                    :developed, :development, :notes)""")
        result = connection.execute(qry,
            userID = userID,
            filmID = nextFilmID,
            projectID = projectID,
            cameraID = request.form['camera'],
            title = title,
            fileNo = fileNo,
            fileDate = fileDate,
            filmTypeID = request.form['filmType'],
            iso = request.form['shotISO'],
            loaded = loaded,
            unloaded = unloaded,
            developed = developed,
            development = request.form['development'],
            notes = request.form['notes'])


    qry = text("""SELECT filmID, title, fileNo, fileDate,
        Films.iso AS iso, brand, FilmTypes.name AS filmName,
        exposures,
        Cameras.name AS camera
        FROM Films
        JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN Cameras ON Cameras.cameraID = Films.cameraID
        WHERE projectID = :projectID ORDER BY fileDate""")
    films = connection.execute(qry, projectID=projectID).fetchall()

    filmTypes = get_film_types(connection)

    qry = text("""SELECT cameraID, name FROM Cameras""")
    cameras = connection.execute(qry).fetchall()

    transaction.commit()

    return render_template('project.html',
        binderID = binderID,
        project = project,
        films = films,
        filmTypes = filmTypes,
        cameras = cameras)

# Film Exposures
@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>',  methods = ['POST', 'GET'])
@login_required
def film(binderID, projectID, filmID):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

    if request.method == 'POST':
        if request.form['button'] == 'deleteExposure':
            qry = text("""DELETE FROM Exposures
                WHERE filmID = :filmID
                AND exposureNumber = :exposureNumber
                AND userID = :userID""")
            result = connection.execute(qry,
                filmID = filmID,
                userID = userID,
                exposureNumber = int(request.form['exposureNumber']))

        if request.form['button'] == 'editExposure':
            return redirect('/binders/' + str(binderID)
                + '/projects/' + str(projectID)
                + '/films/' + str(filmID)
                + '/exposure/' + request.form['exposureNumber'])

        if request.form['button'] == 'editFilm':
            fileDate = None
            loaded = None
            unloaded = None
            developed = None

            if request.form['fileDate'] != 'Unknown':
                fileDate = request.form['fileDate']
            if request.form['loaded'] != 'Unknown':
                loaded = request.form['loaded']
            if request.form['unloaded'] != 'Unknown':
                unloaded = request.form['unloaded']
            if request.form['developed'] != 'Unknown':
                developed = request.form['developed']

            qry = text("""UPDATE Films
                SET title = :title,
                    fileNo = :fileNo,
                    fileDate = :fileDate,
                    filmTypeID = :filmTypeID,
                    cameraID = :cameraID,
                    iso = :iso,
                    loaded = :loaded,
                    unloaded = :unloaded,
                    developed = :developed,
                    development = :development,
                    notes = :notes
                WHERE projectID = :projectID
                AND filmID = :filmID
                AND userID = :userID""")
            result = connection.execute(qry,
                projectID = projectID,
                filmID = filmID,
                userID = userID,
                cameraID = request.form['camera'],
                title = request.form['title'],
                fileNo = request.form['fileNo'],
                fileDate = fileDate,
                filmTypeID = request.form['filmType'],
                iso = request.form['shotISO'],
                loaded = loaded,
                unloaded = unloaded,
                developed = developed,
                development = request.form['development'],
                notes = request.form['notes'])

    film = get_film_details(connection, binderID, projectID, filmID)
    if film is None:
        abort(404)

    qry = text("""SELECT filterID, name FROM Filters
        WHERE userID = :userID""")
    filters = connection.execute(qry, userID = userID).fetchall()

    qry = text("""SELECT CameraLenses.lensID, name FROM CameraLenses
        JOIN Lenses ON Lenses.lensID = CameraLenses.lensID
        WHERE CameraLenses.cameraID = :cameraID
        AND CameraLenses.userID = :userID""")
    lenses = connection.execute(qry, cameraID=film.cameraID, userID=userID).fetchall()

    filmTypes = get_film_types(connection)

    qry = text("""SELECT exposureNumber, shutter, aperture,
        Lenses.name AS lens, flash, metering, subject, notes, development,
        Exposures.iso AS shotISO,
        FilmTypes.name AS filmType, FilmTypes.iso AS filmISO,
        FilmBrands.brand AS filmBrand
        FROM Exposures
        LEFT JOIN Lenses ON Lenses.lensID = Exposures.lensID
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Exposures.filmTypeID
        LEFT OUTER JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE filmID = :filmID
        AND Exposures.userID = :userID""")
    exposuresResult = connection.execute(qry, filmID=filmID, userID=userID).fetchall()
    exposures = result_to_dict(exposuresResult)
    for exposure in exposures:
        qry = text("""SELECT code FROM ExposureFilters
            JOIN Filters ON Filters.filterID = ExposureFilters.filterID
            WHERE filmID = :filmID
            AND exposureNumber = :exposureNumber
            AND ExposureFilters.userID = :userID""")
        filtersResult = connection.execute(qry, filmID=filmID,
            userID = userID,
            exposureNumber = exposure['exposureNumber']).fetchall()
        exposureFilters = result_to_dict(filtersResult)
        exposure['filters'] = exposureFilters

    qry = text("""SELECT MAX(exposureNumber) AS max FROM Exposures
        WHERE filmID = :filmID AND userID = :userID""")
    lastExposureResult = connection.execute(qry, filmID=filmID, userID=userID).first()
    if not lastExposureResult[0]:
        last_exposure = 0
    else:
        last_exposure = lastExposureResult[0]

    if request.args.get('print'):
        print_view = True
        if film.filmSize == '35mm':
            template = 'film/35mm-print.html'
        if film.filmSize == '120':
            template = 'film/120-print.html'
        if film.filmSize == '4x5':
            template = 'film/lf-print.html'
        if film.filmSize == '8x10':
            template = 'film/lf-print.html'
    elif request.args.get('edit'):
        qry = text("""SELECT filmTypeID, cameraID FROM Films
            WHERE filmID = :filmID
            AND userID = :userID""")
        filmDetailsResult = connection.execute(qry, filmID=filmID, userID=userID).first()
        filmTypeID = filmDetailsResult[0]
        cameraID = filmDetailsResult[1]

        qry = text("""SELECT cameraID, name FROM Cameras
            WHERE userID = :userID""")
        cameras = connection.execute(qry, userID=userID).fetchall()
        transaction.commit()
        return render_template('film/edit-film.html',
            binderID=binderID,
            film=film, filmTypeID=filmTypeID, cameraID=cameraID,
            filmTypes=filmTypes, cameras=cameras)
    else:
        print_view = False
        if film.filmSize == '35mm':
            template = 'film/35mm.html'
        if film.filmSize == '120':
            template = 'film/120.html'
        if film.filmSize == '4x5':
            template = 'film/lf.html';
        if film.filmSize == '8x10':
            template = 'film/lf.html';

    # New Exposure (for next entry)
    exposure = {
        'exposureNumber':  last_exposure + 1
    }
    transaction.commit()
    return render_template(template,
        binderID=binderID, projectID=projectID, filmID=filmID,
        film=film, filters=filters, lenses=lenses, exposures=exposures,
        last_exposure=last_exposure, exposure=exposure, print_view=print_view,
        filmTypes=filmTypes,
        view='exposures')

# Edit Exposure
@app.route('/binders/<int:binderID>/projects/<int:projectID>/films/<int:filmID>/exposure/<int:exposureNumber>',  methods = ['POST', 'GET'])
@login_required
def expsoure(binderID, projectID, filmID, exposureNumber):
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()
    # Check this is a valid film to show
    qry = text("""SELECT filmID, Films.projectID, Projects.name AS project, brand,
        FilmTypes.name AS filmName, FilmTypes.iso AS filmISO,
        Films.iso AS shotISO, fileNo, fileDate, filmSize, title,
        loaded, unloaded, developed, development, Cameras.name AS camera,
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
        projectID=projectID,
        binderID=binderID,
        filmID=filmID,
        userID=userID).fetchone()
    if film is None:
        abort(404)

    if request.method == 'POST':
        lensID = None
        aperture = None
        metering = None
        flash = 'No'
        filmType = None
        shotISO = None
        subject = None
        development = None
        notes = None
        shutter = None

        if re.search(r'^1\/', request.form['shutter']):
            shutter = re.sub(r'^1\/', r'', request.form['shutter'])
        elif re.search(r'"', request.form['shutter']):
            shutter = re.sub(r'"', r'', request.form['shutter'])
        elif request.form['shutter'] == 'B' or request.form['shutter'] == 'Bulb':
            shutter = 0
        elif request.form['shutter'] != '':
            shutter = request.form['shutter']

        if request.form['aperture'] != '':
            aperture = request.form['aperture']

        if request.form['lens'] != '':
            lensID = request.form['lens']

        if request.form['metering'] != '':
            metering = request.form['metering']

        if request.form.get('flash') != None:
            flash = 'Yes'

        if request.form.get('filmType') != '':
            filmType = request.form.get('filmType')

        if request.form.get('shotISO') != '':
            shotISO = request.form.get('shotISO')

        if request.form.get('subject') != '':
            subject = request.form.get('subject')

        if request.form.get('development') != '':
            development = request.form.get('development')

        if request.form.get('notes') != '':
            notes = request.form['notes']

        if request.form['button'] == 'addExposure':
            qry = text("""INSERT INTO Exposures
                (userID, filmID, exposureNumber, lensID, shutter, aperture, filmTypeID, iso, metering, flash, subject, development, notes)
                VALUES (:userID, :filmID, :exposureNumber, :lensID, :shutter, :aperture, :filmType, :shotISO, :metering, :flash, :subject, :development, :notes)""")
            result = connection.execute(qry,
                userID = userID,
                filmID = filmID,
                exposureNumber = request.form['exposureNumber'],
                lensID = lensID,
                shutter = shutter,
                aperture = aperture,
                filmType = filmType,
                shotISO = shotISO,
                metering = metering,
                flash = flash,
                subject = subject,
                development = development,
                notes = notes)

            qry = text("""INSERT INTO ExposureFilters
                (userID, filmID, exposureNumber, filterID)
                VALUES (:userID, :filmID, :exposureNumber, :filterID)""")
            for filterID in request.form.getlist('filters'):
                connection.execute(qry,
                    userID = userID,
                    filmID = filmID,
                    exposureNumber = request.form['exposureNumber'],
                    filterID = filterID)

        if request.form['button'] == 'updateExposure':
            qry = text("""UPDATE Exposures
                SET exposureNumber = :exposureNumberNew,
                    shutter = :shutter,
                    aperture = :aperture,
                    lensID = :lensID,
                    flash = :flash,
                    metering = :metering,
                    notes = :notes,
                    subject = :subject,
                    development = :development,
                    filmTypeID = :filmType,
                    iso = :shotISO
                WHERE filmID = :filmID
                AND exposureNumber = :exposureNumberOld
                AND userID = :userID""")
            connection.execute(qry,
                userID = userID,
                filmID = filmID,
                exposureNumberNew = request.form.get('exposureNumber'),
                exposureNumberOld = exposureNumber,
                shutter = shutter,
                aperture = aperture,
                lensID = lensID,
                flash = flash,
                metering = metering,
                notes = notes,
                subject = subject,
                development = development,
                filmType = filmType,
                shotISO = shotISO)

            qry = text("""DELETE FROM ExposureFilters
                WHERE filmID = :filmID
                AND exposureNumber = :exposureNumber
                AND userID = :userID""")
            connection.execute(qry, filmID = filmID,
                userID = userID,
                exposureNumber = request.form['exposureNumber'])

            qry = text("""INSERT INTO ExposureFilters
                (userID, filmID, exposureNumber, filterID)
                VALUES (:userID, :filmID, :exposureNumber, :filterID)""")
            for filterID in request.form.getlist('filters'):
                connection.execute(qry,
                    userID = userID,
                    filmID = filmID,
                    exposureNumber = request.form['exposureNumber'],
                    filterID = filterID)
        transaction.commit()
        return redirect('/binders/' + str(binderID)
            + '/projects/' + str(projectID)
            + '/films/' + str(filmID))

    qry = text("""SELECT Filters.filterID, Filters.name,
        IF(exposureNumber IS NOT NULL, 'checked', NULL) AS checked
        FROM Filters
        LEFT OUTER JOIN ExposureFilters ON ExposureFilters.filterID = Filters.filterID
            AND Filters.userID = :userID
            AND filmID = :filmID
            AND exposureNumber = :exposureNumber
            AND Filters.userID = :userID""")
    filters = connection.execute(qry,  userID=userID, filmID=filmID, exposureNumber=exposureNumber).fetchall()

    qry = text("""SELECT CameraLenses.lensID, name FROM CameraLenses
        JOIN Lenses ON Lenses.lensID = CameraLenses.lensID
        JOIN Films ON Films.cameraID = CameraLenses.cameraID
        WHERE projectID = :projectID AND filmID = :filmID AND Films.userID = :userID""")
    lenses = connection.execute(qry, projectID=projectID, filmID=filmID, userID=userID).fetchall()

    qry = text("""SELECT exposureNumber, shutter, aperture,
        lensID, flash, notes, metering, subject, development, filmTypeID, iso
        FROM Exposures
        WHERE filmID = :filmID
        AND exposureNumber = :exposureNumber
        AND userID = :userID""")
    exposure = connection.execute(qry,
        filmID=filmID,
        exposureNumber=exposureNumber,
        userID = userID).fetchone()
    qry = text("""SELECT code FROM ExposureFilters
        JOIN Filters ON Filters.filterID = ExposureFilters.filterID
        WHERE filmID = :filmID
        AND exposureNumber = :exposureNumber
        AND ExposureFilters.userID = :userID""")
    filtersResult = connection.execute(qry, filmID=filmID,
        exposureNumber = exposureNumber,
        userID = userID).fetchall()
    exposureFilters = result_to_dict(filtersResult)

    qry = text("""SELECT filmSize FROM Cameras
        JOIN Films On Films.cameraID = Cameras.cameraID
        WHERE filmID = :filmID
        AND Cameras.userID = :userID""")
    film = connection.execute(qry, filmID=filmID, userID=userID).fetchone()
    filmTypes = get_film_types(connection)

    transaction.commit()
    return render_template('film/edit-exposure.html',
        userID=userID,
        binderID=binderID,
        projectID=projectID, filmID=filmID,
        filters=filters, lenses=lenses, exposure=exposure,
        exposureFilters=exposureFilters, film=film, filmTypes=filmTypes)

@app.route('/filmtypes',  methods = ['GET'])
@login_required
def filmtypes():
    filmtypes = get_film_types(engine.connect())
    return render_template('filmtypes.html', filmtypes=filmtypes)

@app.route('/gear',  methods = ['GET', 'POST'])
@login_required
def gear():
    connection = engine.connect()
    transaction = connection.begin()
    userID = current_user.get_id()

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
    return render_template('gear.html', cameras=cameras, filters=filters)
