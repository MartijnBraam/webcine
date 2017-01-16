from flask import Flask
from flask_peewee.db import Database
from celery import Celery

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = Database(app)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
