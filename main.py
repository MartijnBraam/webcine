import pymysql

pymysql.install_as_MySQLdb()

from app import app, db, celery
import indexer
from auth import *
from models import *
from views import *

# mod_wsgi support
application = app

if __name__ == '__main__':
    indexer.index()
    app.run(host='0.0.0.0')
