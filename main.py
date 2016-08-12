import pymysql

pymysql.install_as_MySQLdb()

from app import app, db, celery
import indexer
import metadata
import transcoder
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

    parser.add_argument('--indexer', help='Run indexer', action='store_true', default=False)
    parser.add_argument('--metadata', help='Run metadata fetcher', action='store_true', default=False)
    parser.add_argument('--transcode', help='Scan for media that needs transcoding', action='store_true', default=False)
    parser.add_argument('--transcodeone', help='Transcode one media id')

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    if args.indexer:
        indexer.index()
    if args.transcode:
        transcoder.create_transcode_tasks()
    if args.metadata:
        metadata.update_tvdb_data()
    if args.transcodeone:
        transcoder.transcode_one(args.transcodeone)