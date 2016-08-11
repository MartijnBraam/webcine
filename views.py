import mimetypes

from flask import request, redirect, url_for, render_template, flash, send_file, Response

import os
import re

from app import app
from auth import auth
from models import WatchInfo, SeriesWatchInfo, Media, Series, Actor, SeriesActor, Season


@app.route('/')
@auth.login_required
def homepage():
    user = auth.get_logged_in_user()
    watch_next = list(WatchInfo.select().join(Media).where(
        WatchInfo.user == user and WatchInfo.visible == True and WatchInfo.watched == False).order_by(
        Media.season, Media.episode))

    movies = []
    series = []
    episodes = []
    for watchable in watch_next:
        if watchable.media.type == 'movie':
            movies.append(watchable)
        elif watchable.media.type == 'tvepisode':
            if watchable.media.series.name not in series:
                episodes.append(watchable)
                series.append(watchable.media.series.name)

    episodes = sorted(episodes, key=lambda x: x.media.series.id)

    context = {
        'nothing_to_watch': len(watch_next) == 0,
        'movies': movies,
        'episodes': episodes
    }
    return render_template('home.html', **context)


@app.route('/available-series')
@auth.login_required
def available_series():
    user = auth.get_logged_in_user()
    user_series = list(SeriesWatchInfo.select().where(
        SeriesWatchInfo.user == user and SeriesWatchInfo.visible == True and SeriesWatchInfo.following == False))
    return render_template('available_series.html', series=user_series)


@app.route('/start-series/<int:series_id>')
@auth.login_required
def start_series(series_id):
    user = auth.get_logged_in_user()
    series = Series.get(Series.id == series_id)
    series_media = Media.select().where(Media.series == series)
    for episode in series_media:
        WatchInfo.create(user=user, media=episode)

    watchinfo = SeriesWatchInfo.get(SeriesWatchInfo.series == series, SeriesWatchInfo.user == user)
    watchinfo.following = True
    watchinfo.save()

    return redirect(url_for('homepage'))


@app.route('/cache/<string:type>/<int:id>')
@auth.login_required
def cache(type, id):
    ext = 'jpg'
    file = 'storage/cache/{}/{}.{}'.format(type, id, ext)
    return send_file(file)


@app.route('/play/<int:media_id>')
@auth.login_required
def play_media(media_id):
    user = auth.get_logged_in_user()
    media = Media.get(Media.id == media_id)
    watchinfo = WatchInfo.get(WatchInfo.user == user, WatchInfo.media == media)
    return render_template('play.html', media=media, watchinfo=watchinfo)


@app.route('/progress/<int:media_id>/<int:progress>')
@auth.login_required
def progress(media_id, progress):
    user = auth.get_logged_in_user()
    media = Media.get(Media.id == media_id)
    info = WatchInfo().get(WatchInfo.user == user and WatchInfo.media == media)
    info.progress = progress

    if progress > media.length * 0.9:
        info.watched = True

    info.save()
    return '{}'


@app.route('/mark-watched/<int:media_id>')
@auth.login_required
def mark_watched(media_id):
    user = auth.get_logged_in_user()
    media = Media.get(Media.id == media_id)
    info = WatchInfo().get(WatchInfo.user == user and WatchInfo.media == media)
    info.watched = True
    info.save()
    return redirect(url_for('homepage'))


@app.route('/hide/<int:media_id>')
@auth.login_required
def mark_hidden(media_id):
    user = auth.get_logged_in_user()
    media = Media.get(Media.id == media_id)
    info = WatchInfo().get(WatchInfo.user == user and WatchInfo.media == media)
    info.visible = False
    info.save()
    return redirect(url_for('homepage'))


@app.route('/mark-season-watched/<int:media_id>')
@auth.login_required
def mark_season_watched(media_id):
    """ This function does horrible things to your mysql. (n*2)+3 queries"""
    user = auth.get_logged_in_user()
    media = Media.get(Media.id == media_id)
    episodes = list(Media.select().where(Media.series == media.series and Media.season == media.season))
    for episode in episodes:
        try:
            info = WatchInfo().get(WatchInfo.user == user and WatchInfo.media == episode)
            info.watched = True
            info.save()
        except Exception:
            pass
    return redirect(url_for('homepage'))


@app.route('/series-details/<int:series_id>')
@auth.login_required
def series_details(series_id):
    user = auth.get_logged_in_user()
    series = Series.get(Series.id == series_id)
    seasons = Season.get(Season.series == series)
    episodes = list(Media.select().where(Media.series == series).order_by(-Media.season, -Media.episode))
    season_episodes = {}
    for episode in episodes:
        if episode.season not in season_episodes.keys():
            season_episodes[episode.season] = {}
        season_episodes[episode.season][episode.episode] = episode
    actors = SeriesActor.select().join(Actor).where(SeriesActor.series == series)
    return render_template('series-details.html', series=series, season_episodes=season_episodes, actors=actors,
                           seasons=seasons)


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
