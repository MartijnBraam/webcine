import os

from flask import request, redirect, url_for, render_template, send_file

from webcine.app import app
from webcine.models import WatchInfo, SeriesWatchInfo, Media, Series
from webcine.utils.auth import auth


@app.route('/')
@auth.login_required
def homepage():
    user = auth.get_logged_in_user()
    query = WatchInfo.select().join(Media).where(
        (WatchInfo.user == user) & (WatchInfo.visible == True) & (WatchInfo.watched == False)).order_by(
        Media.season, Media.episode)
    watch_next = list(query)

    movies = []
    series = []
    episodes = []
    for watchable in watch_next:
        if watchable.media.type == 'movie':
            if watchable.permissions or user.admin:
                movies.append(watchable)
        elif watchable.media.type == 'tvepisode':
            if watchable.media.series.name not in series:
                episodes.append(watchable)
                series.append(watchable.media.series.name)

    episodes = sorted(episodes, key=lambda x: x.media.series.id)
    movies = sorted(movies, key=lambda x: "{0:03d}-{1}".format(100 - x.progress, x.media.name))
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
        (SeriesWatchInfo.user == user) & (SeriesWatchInfo.visible == True) & (SeriesWatchInfo.following == False) & (
            SeriesWatchInfo.permissions == True)
    ))
    return render_template('available_series.html', series=user_series)


@app.route('/start-series/<int:series_id>')
@auth.login_required
def start_series(series_id):
    user = auth.get_logged_in_user()
    series = Series.get(Series.id == series_id)
    series_media = Media.select().where(Media.series == series)
    for episode in series_media:
        WatchInfo.create(user=user, media=episode)

    try:
        watchinfo = SeriesWatchInfo.get(SeriesWatchInfo.series == series, SeriesWatchInfo.user == user)
    except:
        watchinfo = SeriesWatchInfo.create(series=series, user=user, visible=True, permissions=False, following=False)
    watchinfo.following = True
    watchinfo.save()

    return redirect(url_for('homepage'))


@app.route('/cache/<string:type>/<int:id>')
@auth.login_required
def cache(type, id):
    ext = 'jpg'
    file = '{}/cache/{}/{}.{}'.format(app.config['STORAGE'], type, id, ext)
    if not os.path.isfile(file):
        file = 'static/fallback.png'
    return send_file(file)


@app.route('/mark-watched/<int:media_id>')
@auth.login_required
def mark_watched(media_id):
    user = auth.get_logged_in_user()
    media = Media.get(Media.id == media_id)
    info = WatchInfo().get((WatchInfo.user == user) & (WatchInfo.media == media))
    info.watched = True
    info.save()
    return redirect(url_for('homepage'))


@app.route('/hide/<int:media_id>')
@auth.login_required
def mark_hidden(media_id):
    user = auth.get_logged_in_user()
    media = Media.get(Media.id == media_id)
    info = WatchInfo().get((WatchInfo.user == user) & (WatchInfo.media == media))
    info.visible = False
    info.save()
    return redirect(url_for('homepage'))
