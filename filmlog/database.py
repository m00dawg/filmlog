from filmlog import app

import os, re
import ConfigParser

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini'))

#if(config.get('global', 'docker') == 1):
#    db_url=os.environ.get('FILMLOG_DB_URL')
#else:
#    db_url=config.get('database', 'url')
#app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_DATABASE_URI'] = config.get('database', 'url')

engine = create_engine(config.get('database', 'url'),
    pool_recycle=config.getint('database', 'pool_recycle'))
