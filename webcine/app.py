from flask import Flask
from flask_peewee.db import Database
from webcine.utils.config import get_config

app = Flask(__name__)
app.config.from_object(get_config())
db = Database(app)