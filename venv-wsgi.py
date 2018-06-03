#!/usr/bin/python
# If installing filmlog in a virtualenv and using Apache WSGI, use this
# Be sure to chage the path below to the path of your virtual env
activate_this = '/path/to/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
from filmlog import app as application

