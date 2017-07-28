#!/bin/bash
. venv/bin/activate
export FLASK_APP="filmlog"
export FLASK_DEBUG=1
#cd filmlog
uwsgi --socket 0.0.0.0:8000 --protocol=http -w wsgi

