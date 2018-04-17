from flask import request, render_template, redirect, url_for, Response, session, abort
from sqlalchemy.sql import select, text, func
import os, re

from flask_login import LoginManager, login_required, current_user, login_user, UserMixin

from filmlog import app
from filmlog import database
from filmlog import functions
from filmlog import users
from filmlog import filmstock
from filmlog import darkroom

engine = database.engine

@app.route('/',  methods = ['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

# Binder List
@app.route('/binders',  methods = ['POST', 'GET'])
@login_required
def binders():
    if request.method == 'POST':
        qry = text("""INSERT INTO Binders
            (name, userID) VALUES (:name, :userID)""")
        result = engine.execute(qry,
            name = request.form['name'],
            userID = current_user.get_id())
    qry = text("""SELECT binderID, name, projectCount, createdOn
        FROM Binders WHERE userID = :userID""")
    binders = engine.execute(qry, userID = current_user.get_id()).fetchall()
    return render_template('binders.html', binders=binders)

# Project List
@app.route('/binders/<int:binderID>/projects',  methods = ['POST', 'GET'])
@login_required
def projects(binderID):
    # Get current binder (and check to make sure a user isn't trying to
    # access someone else's binder)
    qry = text("""SELECT binderID, name FROM Binders
        WHERE binderID = :binderID AND userID = :userID""")
    binder = engine.execute(qry,
        binderID=binderID,
        userID=current_user.get_id()).fetchone()
    if binder is None:
        abort(404)

    if request.method == 'POST':
        qry = text("""INSERT INTO Projects
            (binderID, name) VALUES (:binderID, :name)""")
        result = engine.execute(qry,
            binderID = binderID,
            name = request.form['name'])

    qry = text("""SELECT projectID, name, filmCount, createdOn FROM Projects
        WHERE binderID = :binderID""")
    projects = engine.execute(qry, binderID=binderID).fetchall()
    return render_template('projects.html', binder=binder, binderID=binderID, projects=projects)

# Project Films List
@app.route('/binders/<int:binderID>/projects/<int:projectID>',  methods = ['POST', 'GET'])
@login_required
def project(binderID, projectID):
    qry = text("""SELECT projectID, Projects.name AS name
        FROM Projects
        JOIN Binders ON Binders.binderID = Projects.binderID
        WHERE projectID = :projectID
        AND Projects.binderID = :binderID
        AND userID = :userID""")
    project = engine.execute(qry,
        projectID = projectID,
        binderID = binderID,
        userID = current_user.get_id()).fetchone()
    if project is None:
        abort(404)

    if request.method == 'POST':
        fileDate = None
        loaded = None
        unloaded = None
        developed = None

        if request.form['fileDate'] != '':
            fileDate = request.form['fileDate']
        if request.form['loaded'] != '':
            loaded = request.form['loaded']
        if request.form['unloaded'] != '':
            unloaded = request.form['unloaded']
        if request.form['developed'] != '':
            developed = request.form['developed']

        qry = text("""INSERT INTO Films
            (projectID, cameraID, title, fileNo, fileDate, filmTypeID, iso,
             loaded, unloaded, developed, development, notes)
            VALUES (:projectID, :cameraID, :title, UPPER(:fileNo),
                    :fileDate, :filmTypeID, :iso, :loaded, :unloaded,
                    :developed, :development, :notes)""")
        result = engine.execute(qry,
            projectID = projectID,
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

    qry = text("""SELECT filmID, title, fileNo, fileDate,
        Films.iso AS iso, brand, FilmTypes.name AS filmName,
        exposures,
        Cameras.name AS camera
        FROM Films
        JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN Cameras ON Cameras.cameraID = Films.cameraID
        WHERE projectID = :projectID ORDER BY fileDate""")
    films = engine.execute(qry, projectID=projectID).fetchall()

    qry = text("""SELECT filmTypeID, brand, name, iso FROM FilmTypes
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        ORDER BY brand, name""")
    filmTypes = engine.execute(qry).fetchall()

    qry = text("""SELECT cameraID, name FROM Cameras""")
    cameras = engine.execute(qry).fetchall()

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
    film = engine.execute(qry,
        projectID=projectID,
        binderID=binderID,
        filmID=filmID,
        userID=current_user.get_id()).fetchone()
    if film is None:
        abort(404)

    if request.method == 'POST':
        if request.form['button'] == 'deleteExposure':
            qry = text("""DELETE FROM Exposures
                WHERE filmID = :filmID
                AND exposureNumber = :exposureNumber""")
            result = engine.execute(qry,
                filmID = filmID,
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
                WHERE projectID = :projectID AND filmID = :filmID""")
            result = engine.execute(qry,
                projectID = projectID,
                filmID = filmID,
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

    qry = text("""SELECT filterID, name FROM Filters
        WHERE userID = :userID""")
    filters = engine.execute(qry, userID = current_user.get_id()).fetchall()

    qry = text("""SELECT CameraLenses.lensID, name FROM CameraLenses
        JOIN Lenses ON Lenses.lensID = CameraLenses.lensID
        WHERE CameraLenses.cameraID = :cameraID""")
    lenses = engine.execute(qry, cameraID=film.cameraID).fetchall()

    qry = text("""SELECT filmTypeID, brand, name, iso FROM FilmTypes
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID""")
    filmTypes = engine.execute(qry).fetchall()

    qry = text("""SELECT exposureNumber, shutter, aperture,
        Lenses.name AS lens, flash, metering, subject, notes, development,
        Exposures.iso AS shotISO,
        FilmTypes.name AS filmType, FilmTypes.iso AS filmISO,
        FilmBrands.brand AS filmBrand
        FROM Exposures
        LEFT JOIN Lenses ON Lenses.lensID = Exposures.lensID
        LEFT OUTER JOIN FilmTypes ON FilmTypes.filmTypeID = Exposures.filmTypeID
        LEFT OUTER JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        WHERE filmID = :filmID""")
    exposuresResult = engine.execute(qry, filmID=filmID).fetchall()
    exposures = functions.result_to_dict(exposuresResult)
    for exposure in exposures:
        qry = text("""SELECT code FROM ExposureFilters
            JOIN Filters ON Filters.filterID = ExposureFilters.filterID
            WHERE filmID = :filmID AND exposureNumber = :exposureNumber""")
        filtersResult = engine.execute(qry, filmID=filmID,
            exposureNumber = exposure['exposureNumber']).fetchall()
        exposureFilters = functions.result_to_dict(filtersResult)
        exposure['filters'] = exposureFilters

    qry = text("""SELECT MAX(exposureNumber) AS max FROM Exposures
        WHERE filmID = :filmID""")
    lastExposureResult = engine.execute(qry, filmID=filmID).first()
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
        qry = text("""SELECT filmTypeID, cameraID FROM Films WHERE filmID = :filmID""")
        filmDetailsResult = engine.execute(qry, filmID=filmID).first()
        filmTypeID = filmDetailsResult[0]
        cameraID = filmDetailsResult[1]

        qry = text("""SELECT cameraID, name FROM Cameras""")
        cameras = engine.execute(qry).fetchall()

        return render_template('film/edit.html',
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
    film = engine.execute(qry,
        projectID=projectID,
        binderID=binderID,
        filmID=filmID,
        userID=current_user.get_id()).fetchone()
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
                (filmID, exposureNumber, lensID, shutter, aperture, filmTypeID, iso, metering, flash, subject, development, notes)
                VALUES (:filmID, :exposureNumber, :lensID, :shutter, :aperture, :filmType, :shotISO, :metering, :flash, :subject, :development, :notes)""")
            result = engine.execute(qry,
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
                (filmID, exposureNumber, filterID)
                VALUES (:filmID, :exposureNumber, :filterID)""")
            for filterID in request.form.getlist('filters'):
                engine.execute(qry,
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
                    development = :development
                WHERE filmID = :filmID
                AND exposureNumber = :exposureNumberOld""")
            engine.execute(qry,
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
                development = development)

            qry = text("""DELETE FROM ExposureFilters
                WHERE filmID = :filmID
                AND exposureNumber = :exposureNumber""")
            engine.execute(qry, filmID = filmID,
            exposureNumber = request.form['exposureNumber'])

            qry = text("""INSERT INTO ExposureFilters
                (filmID, exposureNumber, filterID)
                VALUES (:filmID, :exposureNumber, :filterID)""")
            for filterID in request.form.getlist('filters'):
                engine.execute(qry,
                    filmID = filmID,
                    exposureNumber = request.form['exposureNumber'],
                    filterID = filterID)
        return redirect('/binders/' + str(binderID)
            + '/projects/' + str(projectID)
            + '/films/' + str(filmID))

    qry = text("""SELECT Filters.filterID, Filters.name,
        IF(exposureNumber IS NOT NULL, 'checked', NULL) AS checked
        FROM Filters
        LEFT OUTER JOIN ExposureFilters ON ExposureFilters.filterID = Filters.filterID
            AND filmID = :filmID AND exposureNumber = :exposureNumber""")
    filters = engine.execute(qry, filmID=filmID, exposureNumber=exposureNumber).fetchall()

    qry = text("""SELECT CameraLenses.lensID, name FROM CameraLenses
        JOIN Lenses ON Lenses.lensID = CameraLenses.lensID
        JOIN Films ON Films.cameraID = CameraLenses.cameraID
        WHERE projectID = :projectID AND filmID = :filmID""")
    lenses = engine.execute(qry, projectID=projectID, filmID=filmID).fetchall()

    qry = text("""SELECT exposureNumber, shutter, aperture,
        lensID, flash, notes, metering
        FROM Exposures
        WHERE filmID = :filmID AND exposureNumber = :exposureNumber""")
    exposure = engine.execute(qry,
        filmID=filmID, exposureNumber=exposureNumber).fetchone()
    qry = text("""SELECT code FROM ExposureFilters
        JOIN Filters ON Filters.filterID = ExposureFilters.filterID
        WHERE filmID = :filmID AND exposureNumber = :exposureNumber""")
    filtersResult = engine.execute(qry, filmID=filmID,
        exposureNumber = exposureNumber).fetchall()
    exposureFilters = functions.result_to_dict(filtersResult)

    qry = text("""SELECT filmSize FROM Cameras
        JOIN Films On Films.cameraID = Cameras.cameraID
        WHERE filmID = :filmID""")
    filmSize = engine.execute(qry, filmID=filmID).fetchone()

    return render_template('film/edit-exposure.html',
        binderID=binderID,
        projectID=projectID, filmID=filmID,
        filters=filters, lenses=lenses, exposure=exposure,
        exposureFilters=exposureFilters, filmSize=filmSize)

@app.route('/filmtypes',  methods = ['GET'])
@login_required
def filmtypes():
    qry = text("""SELECT filmTypeID, brand, name, iso, kind
                  FROM FilmTypes
                  JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
                  ORDER BY brand, name, iso""")
    filmtypes = engine.execute(qry).fetchall()
    return render_template('filmtypes.html', filmtypes=filmtypes)

@app.route('/gear',  methods = ['GET', 'POST'])
@login_required
def gear():
    if request.method == 'POST':
        qry = text("""INSERT INTO Cameras
            (name, filmSize, userID) VALUES (:name, :filmSize, :userID)""")
        result = engine.execute(qry,
            name = request.form['name'],
            filmSize = request.form['filmSize'],
            userID = current_user.get_id())

    qry = text("""SELECT cameraID, name, filmSize
        FROM Cameras
        WHERE userID = :userID""")
    cameras = engine.execute(qry, userID = current_user.get_id()).fetchall()

    qry = text("""SELECT filterID, name, code, factor
                  FROM Filters
                  WHERE userID = :userID""")
    filters = engine.execute(qry, userID = current_user.get_id()).fetchall()
    return render_template('gear.html', cameras=cameras, filters=filters)
