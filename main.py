from app import app, db

import indexer
from auth import *
from models import *
from views import *

if __name__ == '__main__':
    indexer.index()
    app.run()
