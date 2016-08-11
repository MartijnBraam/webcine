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
    import argparse
    import logging

    parser = argparse.ArgumentParser(description="Webcine console tool")
    parser.add_argument('--verbose', '-v', help='More verbose messages', action='store_true', default=False)
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    indexer.index()
