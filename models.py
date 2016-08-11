from flask_peewee.auth import BaseUser
from peewee import *

from hashlib import md5

from app import db


class User(db.Model, BaseUser):
    username = CharField()
    password = CharField()
    admin = BooleanField(default=False)
    active = BooleanField(default=True)
    email = CharField()

    def gravatar_url(self, size=80):
        return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
               (md5(self.email.strip().lower().encode('utf-8')).hexdigest(), size)


class Library(db.Model):
    name = CharField(unique=True)
    type = CharField(max_length=10)
    structure = CharField()


class Actor(db.Model):
    name = CharField(unique=True)


class Series(db.Model):
    name = CharField()
    tvdb_id = IntegerField(unique=True)
    description = TextField(null=True)
    genre = CharField(null=True)
    mpaa = CharField(null=True)
    studio = CharField(null=True)


class Season(db.Model):
    series = ForeignKeyField(Series)
    number = IntegerField()
    episodes = IntegerField()
    description = TextField(null=True)

    class Meta:
        indexes = (
            (('series', 'number'), True),
        )


class Media(db.Model):
    type = CharField(max_length=10)
    length = IntegerField(null=True)
    library = ForeignKeyField(Library)
    path = CharField()
    description = TextField(null=True)
    playable = BooleanField(default=True)
    series = ForeignKeyField(Series, null=True)
    season = IntegerField(null=True)
    episode = IntegerField(null=True)
    dual_episode = BooleanField(default=False)
    part = IntegerField(null=True)
    name = CharField()

    class Meta:
        order_by = ('series', 'episode', 'name', 'part')


class MediaActor(db.Model):
    media = ForeignKeyField(Media)
    actor = ForeignKeyField(Actor)
    personage = CharField(null=True)


class SeriesActor(db.Model):
    series = ForeignKeyField(Series)
    actor = ForeignKeyField(Actor)
    personage = CharField(null=True)


class WatchInfo(db.Model):
    user = ForeignKeyField(User)
    media = ForeignKeyField(Media)
    watched = BooleanField(default=False)
    progress = IntegerField(default=0)
    visible = BooleanField(default=True)
    permissions = BooleanField(default=False)


class SeriesWatchInfo(db.Model):
    user = ForeignKeyField(User)
    series = ForeignKeyField(Series)
    visible = BooleanField(default=True)
    following = BooleanField(default=False)
    permissions = BooleanField(default=False)


if not User.table_exists():
    User.create_table()
    admin = User.create(username='admin', password='', admin=True, active=True, email='admin@example.com')
    admin.set_password('admin')
    admin.save()
if not Library.table_exists():
    Library.create_table()
    Library.create(name='tv', type='tvseries', structure='sickbeard')
if not Series.table_exists():
    Series.create_table()
if not Season.table_exists():
    Season.create_table()
if not Media.table_exists():
    Media.create_table()
if not WatchInfo.table_exists():
    WatchInfo.create_table()
if not Actor.table_exists():
    Actor.create_table()
if not MediaActor.table_exists():
    MediaActor.create_table()
if not SeriesActor.table_exists():
    SeriesActor.create_table()
if not SeriesWatchInfo.table_exists():
    SeriesWatchInfo.create_table()
