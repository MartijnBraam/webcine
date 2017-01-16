import os
import sys
import configparser
import logging


def get_config(app):
    paths = [
        './webcine.conf',
        '/etc/webcine.conf'
    ]
    for path in paths:
        logging.debug('Checking {}'.format(path))
        if os.path.isfile(path):
            logging.info('Using config {}'.format(path))
            parser = configparser.ConfigParser()
            parser.read(path)

            config_obj = {
                'SECRET_KEY': parser.get('webcine', 'secret_key'),
                'DATABASE': {
                    'name': parser.get('database', 'name'),
                    'engine': 'peewee.MySQLDatabase',
                    'host': parser.get('database', 'host'),
                    'user': parser.get('database', 'user'),
                    'password': parser.get('database', 'password')
                },
                'QUEUE': parser.get('rabbitmq', 'url'),
            }

            app.config.update(config_obj)
            return

    logging.critical('Config file not found. Exiting')
    sys.exit(1)
