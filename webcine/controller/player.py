import mimetypes
import os
import re

from flask import request, render_template, send_file, Response

from webcine.app import app
from webcine.models import WatchInfo, Media, TranscodedMedia
from webcine.utils.auth import auth


@app.route('/play/<int:media_id>', defaults={'transcode_id': None})
@app.route('/play/<int:media_id>/<int:transcode_id>', endpoint='play_media_transcoded')
@auth.login_required
def play_media(media_id, transcode_id):
    user = auth.get_logged_in_user()
    media = Media.get(Media.id == media_id)
    watchinfo = WatchInfo.get(WatchInfo.user == user, WatchInfo.media == media)
    transcodes = TranscodedMedia.select().where(TranscodedMedia.media == media)
    src = '/stream/{}'.format(media.path)
    if transcode_id:
        src = '/stream/transcoded/{}/{}.mkv'.format(transcode_id, media.id)
    return render_template('play.html', media=media, watchinfo=watchinfo, transcodes=transcodes,
                           transcode_id=transcode_id, src=src)


@app.route('/progress/<int:media_id>/<int:progress>')
@auth.login_required
def progress(media_id, progress):
    user = auth.get_logged_in_user()
    media = Media.get(Media.id == media_id)
    info = WatchInfo().get((WatchInfo.user == user) & (WatchInfo.media == media))
    info.progress = progress

    if progress > media.length * 0.9:
        info.watched = True

    info.save()
    return '{}'


@app.route('/stream/<path:filename>')
def storage(filename):
    return send_file_partial(filename)


def send_file_partial(path):
    """
        Simple wrapper around send_file which handles HTTP 206 Partial Content
        (byte ranges)
        TODO: handle all send_file args, mirror send_file's error handling
        (if it has any)
    """
    print("Start stream response")
    range_header = request.headers.get('Range', None)
    if not range_header: return send_file(path)

    size = os.path.getsize(path)
    byte1, byte2 = 0, None

    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()

    if g[0]: byte1 = int(g[0])
    if g[1]: byte2 = int(g[1])

    length = size - byte1
    if byte2 is not None:
        length = byte2 - byte1

    with open(path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)

    rv = Response(data,
                  206,
                  mimetype=mimetypes.guess_type(path)[0],
                  direct_passthrough=True)
    rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))
    rv.headers.add('Keep-Alive', 'no')
    print("Stream done")
    return rv
