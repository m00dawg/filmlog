from flask import request, render_template, redirect, url_for, flash, abort
from filmlog import app


@app.route('/help', methods=['GET', 'POST'])
def help():
    return render_template('help/index.html')
