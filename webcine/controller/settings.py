from flask import render_template, request, redirect, url_for

from webcine.app import app
from webcine.models import User, SeriesWatchInfo, Series, WatchInfo, Media
from webcine.utils.auth import auth


@app.route('/admin/users')
@auth.admin_required
def admin_users():
    users = list(User.select())
    return render_template('settings/users.html', users=users)


@app.route('/admin/save/user', methods=['POST'])
@auth.admin_required
def admin_save_user():
    payload = request.json
    entity = User.get(User.id == payload['id'])
    entity.username = payload['username']
    entity.email = payload['email']
    entity.admin = payload['admin']
    entity.active = payload['active']

    if payload['password'] != "":
        entity.set_password(payload['password'])

    entity.save()
    return '{}'


@app.route('/admin/create/user', methods=['POST'])
@auth.admin_required
def admin_create_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    active = 'active' in request.form
    admin = 'admin' in request.form

    user = User.create(username=username, email=email, active=active, admin=admin)
    user.set_password(password)
    user.save()
    return redirect(url_for('admin_users'))


@app.route('/admin/series')
@auth.admin_required
def admin_series():
    users = list(User.select())
    watchinfo = {}
    for wi in SeriesWatchInfo.select():
        if wi.series.id not in watchinfo:
            watchinfo[wi.series.id] = {}
        watchinfo[wi.series.id][wi.user.id] = wi

    series = {}
    for s in Series.select():
        series[s.id] = s

    return render_template('settings/series.html', users=users, watchinfo=watchinfo, series=series)


@app.route('/admin/movies')
@auth.admin_required
def admin_movies():
    users = list(User.select())
    watchinfo = {}
    for wi in WatchInfo.select():
        if wi.media.id not in watchinfo:
            watchinfo[wi.media.id] = {}
        watchinfo[wi.media.id][wi.user.id] = wi

    movies = {}
    for m in Media.select().where(Media.series.is_null()):
        movies[m.id] = m

    for wi in list(watchinfo.keys()):
        if wi not in movies.keys():
            del watchinfo[wi]

    return render_template('settings/movies.html', users=users, watchinfo=watchinfo, movies=movies)


@app.route('/admin/series/set/<int:series_id>/<int:user_id>/<state>')
@auth.admin_required
def admin_series_set_permission(series_id, user_id, state):
    series = Series.get(Series.id == series_id)
    user = User.get(User.id == user_id)

    try:
        watchinfo = SeriesWatchInfo.get((SeriesWatchInfo.series == series) & (SeriesWatchInfo.user == user))
        watchinfo.permissions = state == 'on'
        watchinfo.save()
    except:
        permissions = state == 'on'
        watchinfo = SeriesWatchInfo.create(series=series, user=user, visible=True, following=False,
                                           permissions=permissions)
        watchinfo.save()
    return '{}'


@app.route('/admin/movies/set/<int:media_id>/<int:user_id>/<state>')
@auth.admin_required
def admin_media_set_permission(media_id, user_id, state):
    user = User.get(User.id == user_id)
    media = Media.get(Media.id == media_id)

    try:
        watchinfo = WatchInfo.get((WatchInfo.media == media_id) & (WatchInfo.user == user))
        watchinfo.permissions = state == 'on'
        watchinfo.save()
    except:
        permissions = state == 'on'
        watchinfo = WatchInfo.create(media=media, user=user, visible=True, permissions=permissions)
        watchinfo.save()
    return '{}'
