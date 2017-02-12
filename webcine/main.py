import pymysql

pymysql.install_as_MySQLdb()

from webcine.utils import metadata, indexer, cleaner
from webcine.controller.views import *
from webcine.controller.settings import *
from webcine.controller.status import *

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
    parser.add_argument('--transcodeone', help='Transcode one media id', type=int)
    parser.add_argument('--cleanup', help='Clean various database inconsistencies', action='store_true', default=False)

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
    if args.cleanup:
        cleaner.remove_broken_media()
