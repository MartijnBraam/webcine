import os

import requests

import webcine.app
from webcine.app import app

from webcine.models import TranscodingSettings, Media, TranscodedMedia


def create_transcode_task(media, settings):
    existing = list(
        TranscodedMedia.select().where((TranscodedMedia.media == media) & (TranscodedMedia.settings == settings)))

    if len(existing) == 0:
        tm = TranscodedMedia.create(media=media, settings=settings, error='')
    else:
        print(existing)
        print('Database row already exists for this media file. Re-adding task to transode queue only')
        tm = existing[0]

    target_file = '{}/transcoded/{}/{}.mp4'.format(app.config['STORAGE'], settings.profile, media.id)
    if not os.path.isdir(os.path.dirname(target_file)):
        os.makedirs(os.path.dirname(target_file))

    task = {
        'id': tm.id,
        'source': media.path,
        'profile': settings.profile,
        'destination': target_file
    }
    config = webcine.app.app.config['TRANSCODED']
    requests.post('{}jobs'.format(config['url']), json=task, auth=(config['username'], config['password']))


def finished_transcode_task(id, speedfactor):
    tm = TranscodedMedia.get(TranscodedMedia.id == id)
    tm.done = True
    tm.speedfactor = speedfactor
    tm.save()


def failed_transcode_task(id):
    tm = TranscodedMedia.get(TranscodedMedia.id == id)
    tm.done = False
    tm.error = "Transcoding failed"
    tm.save()


def progress_transcode_task(id, progress):
    tm = TranscodedMedia.get(TranscodedMedia.id == id)
    tm.progress = progress
    tm.save()


def transcode_one(id):
    media = Media.get(Media.id == id)
    for setting in TranscodingSettings.select():
        print("Transcode {} to {}".format(media.name, setting.profile))

        create_transcode_task(media, setting)


def create_transcode_tasks():
    settings = list(TranscodingSettings.select())
    for media in Media.select():
        for setting in settings:
            try:
                TranscodedMedia.get(TranscodedMedia.media == media, TranscodedMedia.settings == setting)
            except:
                print("Transcode {} to {}".format(media.name, setting.profile))
                create_transcode_task(media, setting)
