import os
from flask import send_from_directory, flash, abort
from sqlalchemy.sql import select, text, func
from PIL import Image
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_required, current_user, login_user, UserMixin
from filmlog import app
from filmlog import database
from shutil import rmtree

def is_file_allowed(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def delete_file(request, connection, transaction, fileID):
    app.logger.info('Delete file')
    userID = current_user.get_id()
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'],
            str(userID), str(fileID))
        app.logger.debug('filepath, %s', filepath)
        os.path.isfile(filepath)
        rmtree(filepath)
    except Exception:
        app.logger.debug('Exception and Rollback')
        transaction.rollback()
        abort(400)
    app.logger.debug('Remove file from database')
    qry = text("""DELETE FROM Files WHERE userID=:userID AND fileID=:fileID""")
    connection.execute(qry,
        fileID = fileID,
        userID = userID)
    return True

def upload_file(request, connection, transaction, fileID):
    app.logger.info('Upload file')
    userID = current_user.get_id()
    if 'file' not in request.files:
        flash('File missing')
    file = request.files['file']
    if file.filename == '':
        flash('File missing')
    if file and is_file_allowed(file.filename):
        filename = secure_filename(file.filename)
        try:
            directory = os.path.join(app.config['UPLOAD_FOLDER'],
                str(userID), str(fileID))
            if not os.path.exists(directory):
                os.makedirs(directory)
            file.save(os.path.join(directory + "/full.jpg"))
            generate_thumbnail(fileID)
            qry = text("""INSERT INTO Files (fileID, userID)
                VALUES (:fileID, :userID)""")
            connection.execute(qry,
                fileID = fileID,
                userID = userID)
        except Exception:
            app.logger.debug('Exception and Rollback')
            transaction.rollback()
            abort(400)
    return True

def generate_thumbnail(fileID):
    userID = current_user.get_id()
    fullsize = os.path.join(app.config['UPLOAD_FOLDER'], str(userID), str(fileID), "full.jpg")
    size = int(app.config['THUMBNAIL_SIZE']), int(app.config['THUMBNAIL_SIZE'])
    image = Image.open(fullsize)
    image.thumbnail(size, Image.ANTIALIAS)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], str(userID), str(fileID), "thumb.jpg"))

@app.route('/files/thumb/<int:fileID>')
@login_required
def get_thumbnail(fileID):
    userID = current_user.get_id()
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        str(userID) + "/" + str(fileID) + "/thumb.jpg")

@app.route('/files/full/<int:fileID>')
@login_required
def get_fullsize(fileID):
    userID = current_user.get_id()
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        str(userID) + "/" + str(fileID) + "/full.jpg")
