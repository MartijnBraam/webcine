from flask import Flask
from flask_peewee.db import Database
from webcine.utils.config import get_config

app = Flask(__name__)
get_config(app)
db = Database(app)