from flask_peewee.auth import Auth

from webcine.app import app, db
from webcine.models import User

auth = Auth(app, db, user_model=User)