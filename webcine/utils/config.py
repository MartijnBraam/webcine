import os
import sys
import configparser
import logging

STORAGE_PATH = None


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
                'STORAGE': parser.get('webcine', 'storage')
            }

            app.config.update(config_obj)
            return

    logging.critical('Config file not found. Exiting')
    sys.exit(1)


def get_storage_path():
    global STORAGE_PATH
    if STORAGE_PATH:
        return STORAGE_PATH

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

            STORAGE_PATH = parser.get('webcine', 'storage')

            return STORAGE_PATH
