from flask import request, redirect, url_for, render_template, flash, send_file

from app import app
from auth import auth
from models import WatchInfo, SeriesWatchInfo, Media, Series


@app.route('/')
@auth.login_required
def homepage():
    user = auth.get_logged_in_user()
    watch_next = list(WatchInfo.select().where(
        WatchInfo.user == user and WatchInfo.visible == True and WatchInfo.watched == False))

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
