from flask import request, render_template, redirect, url_for
from sqlalchemy.sql import select, text, func
import os, re

from filmlog import app
#import filmlog.database
from filmlog import database
from filmlog import functions


engine = database.engine

@app.route('/',  methods = ['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

@app.route('/projects',  methods = ['POST', 'GET'])
def projects():
    if request.method == 'POST':
        qry = text("""INSERT INTO Projects
            (name) VALUES (:name)""")
        result = engine.execute(qry,
            name = request.form['name'])
    qry = text("""SELECT projectID, name, filmCount, createdOn FROM Projects""")
    projects = engine.execute(qry).fetchall()
    return render_template('projects.html', projects=projects)

@app.route('/projects/<int:projectID>',  methods = ['POST', 'GET'])
def project(projectID):
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

    qry = text("""SELECT projectID, name FROM Projects WHERE projectID = :projectID""")
    project = engine.execute(qry, projectID=projectID).fetchone()

    qry = text("""SELECT filmID, title, fileNo, fileDate,
        Films.iso AS iso, brand, FilmTypes.name AS filmName,
        exposures,
        Cameras.name AS camera
        FROM Films
        JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        JOIN Cameras ON Cameras.cameraID = Films.cameraID
        WHERE projectID = :projectID ORDER BY fileNo""")
    films = engine.execute(qry, projectID=projectID).fetchall()

    qry = text("""SELECT filmTypeID, brand, name, iso FROM FilmTypes
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        ORDER BY brand, name""")
    filmTypes = engine.execute(qry).fetchall()

    qry = text("""SELECT cameraID, name FROM Cameras""")
    cameras = engine.execute(qry).fetchall()

    return render_template('project.html',
        project = project,
        films = films,
        filmTypes = filmTypes,
        cameras = cameras)

@app.route('/projects/<int:projectID>/films/<int:filmID>',  methods = ['POST', 'GET'])
def film(projectID, filmID):
    if request.method == 'POST':
        if request.form['button'] == 'deleteExposure':
            qry = text("""DELETE FROM Exposures
                WHERE filmID = :filmID
                AND exposureNumber = :exposureNumber""")
            result = engine.execute(qry,
                filmID = filmID,
                exposureNumber = int(request.form['exposureNumber']))

        if request.form['button'] == 'editExposure':
            return redirect('/projects/' + str(projectID)
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

        if request.form['button'] == 'addExposure':
            lensID = None
            shutter = None
            aperture = None
            metering = None
            flash = 'No'
            subject = None
            development = None
            notes = None

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

            if request.form['subject'] != '':
                subject = request.form['subject']

            if request.form['development'] != '':
                development = request.form['development']

            if request.form['notes'] != '':
                notes = request.form['notes']

            qry = text("""INSERT INTO Exposures
                (filmID, exposureNumber, lensID, shutter, aperture, metering, flash, subject, development, notes)
                VALUES (:filmID, :exposureNumber, :lensID, :shutter, :aperture, :metering, :flash, :subject, :development, :notes)""")
            result = engine.execute(qry,
                filmID = filmID,
                exposureNumber = request.form['exposureNumber'],
                lensID = lensID,
                shutter = shutter,
                aperture = aperture,
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

    # Reads
    qry = text("""SELECT filmID, Films.projectID, Projects.name AS project, brand,
        FilmTypes.name AS filmName, FilmTypes.iso AS filmISO,
        Films.iso AS shotISO, fileNo, fileDate, filmSize, title,
        loaded, unloaded, developed, development, Cameras.name AS camera,
        Cameras.cameraID AS cameraID, notes
        FROM Films
        JOIN Projects ON Projects.projectID = Films.projectID
        JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        LEFT JOIN Cameras ON Cameras.cameraID = Films.cameraID
        WHERE Films.projectID = :projectID AND filmID = :filmID""")
    film = engine.execute(qry, projectID=projectID, filmID=filmID).fetchone()

    # If we do not find a roll of film for the project, bail out so we
    # don't display any exposures. Preventing shenaigans with cross
    # project access.
    if not film:
        abort(404)

    qry = text("""SELECT filterID, name FROM Filters""")
    filters = engine.execute(qry).fetchall()

    qry = text("""SELECT CameraLenses.lensID, name FROM CameraLenses
        JOIN Lenses ON Lenses.lensID = CameraLenses.lensID
        WHERE CameraLenses.cameraID = :cameraID""")
    lenses = engine.execute(qry, cameraID=film.cameraID).fetchall()

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
        last_exposure = None
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

        qry = text("""SELECT filmTypeID, brand, name, iso FROM FilmTypes
            JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID""")
        filmTypes = engine.execute(qry).fetchall()

        qry = text("""SELECT cameraID, name FROM Cameras""")
        cameras = engine.execute(qry).fetchall()

        return render_template('film/edit.html',
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
    return render_template(template,
        film=film, filters=filters, lenses=lenses, exposures=exposures,
        last_exposure=last_exposure, print_view=print_view)

@app.route('/projects/<int:projectID>/films/<int:filmID>/prints',  methods = ['POST', 'GET'])
def prints(projectID, filmID):

    # Stolen from film route - needs to be a function?
    # Reads
    qry = text("""SELECT filmID, Films.projectID, Projects.name AS project, brand,
        FilmTypes.name AS filmName, FilmTypes.iso AS filmISO,
        Films.iso AS shotISO, fileNo, fileDate, filmSize, title,
        loaded, unloaded, developed, development, Cameras.name AS camera,
        Cameras.cameraID AS cameraID, notes
        FROM Films
        JOIN Projects ON Projects.projectID = Films.projectID
        JOIN FilmTypes ON FilmTypes.filmTypeID = Films.filmTypeID
        JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
        LEFT JOIN Cameras ON Cameras.cameraID = Films.cameraID
        WHERE Films.projectID = :projectID AND filmID = :filmID""")
    film = engine.execute(qry, projectID=projectID, filmID=filmID).fetchone()

    # If we do not find a roll of film for the project, bail out so we
    # don't display any exposures. Preventing shenaigans with cross
    # project access.
    if not film:
        abort(404)

    return render_template('film/prints.html', film=film)

@app.route('/projects/<int:projectID>/films/<int:filmID>/exposure/<int:exposureNumber>',  methods = ['POST', 'GET'])
def expsoure(projectID, filmID, exposureNumber):
    qry = text("""SELECT filterID, name FROM Filters""")
    filters = engine.execute(qry).fetchall()

    qry = text("""SELECT cameraID FROM Films
        WHERE projectID = :projectID AND filmID = :filmID""")
    cameraID = engine.execute(qry, projectID=projectID, filmID=filmID).fetchone()

    qry = text("""SELECT CameraLenses.lensID, name FROM CameraLenses
        JOIN Lenses ON Lenses.lensID = CameraLenses.lensID
        WHERE CameraLenses.cameraID = :cameraID""")
    lenses = engine.execute(qry, cameraID=cameraID).fetchall()

    qry = text("""SELECT shutter, aperture,
        Lenses.name AS lens, flash, notes
        FROM Exposures
        LEFT JOIN Lenses ON Lenses.lensID = Exposures.lensID
        WHERE filmID = :filmID AND exposureNumber = :exposureNumber""")
    exposure = engine.execute(qry,
        filmID=filmID, exposureNumber=exposureNumber).fetchone()
    qry = text("""SELECT code FROM ExposureFilters
        JOIN Filters ON Filters.filterID = ExposureFilters.filterID
        WHERE filmID = :filmID AND exposureNumber = :exposureNumber""")
    filtersResult = engine.execute(qry, filmID=filmID,
        exposureNumber = exposureNumber).fetchall()
    exposureFilters = functions.result_to_dict(filtersResult)

    return render_template('film/exposure.html',
        projectID=projectID, filmID=filmID, exposureNumber=exposureNumber,
        filters=filters, lenses=lenses, exposure=exposure,
        exposureFilters=exposureFilters)


@app.route('/filters',  methods = ['GET'])
def filters():
    qry = text("""SELECT filterID, name, code, factor
                  FROM Filters""")
    filters = engine.execute(qry).fetchall()
    return render_template('filters.html', filters=filters)

@app.route('/filmtypes',  methods = ['GET'])
def filmtypes():
    qry = text("""SELECT filmTypeID, brand, name, iso, kind
                  FROM FilmTypes
                  JOIN FilmBrands ON FilmBrands.filmBrandID = FilmTypes.filmBrandID
                  ORDER BY brand, name, iso""")
    filmtypes = engine.execute(qry).fetchall()
    return render_template('filmtypes.html', filmtypes=filmtypes)

@app.route('/cameras',  methods = ['GET', 'POST'])
def cameras():
    if request.method == 'POST':
        qry = text("""INSERT INTO Cameras
            (name, filmSize) VALUES (:name, :filmSize)""")
        result = engine.execute(qry,
            name = request.form['name'],
            filmSize = request.form['filmSize'])

    qry = text("""SELECT cameraID, name, filmSize FROM Cameras""")
    cameras = engine.execute(qry).fetchall()
    return render_template('cameras.html', cameras=cameras)
