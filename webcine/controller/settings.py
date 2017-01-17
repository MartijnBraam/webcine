from flask import render_template, request, redirect, url_for

from webcine.app import app
from webcine.models import User, SeriesWatchInfo, Series
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
        series[s.id] = series

    return render_template('settings/series.html', users=users, watchinfo=watchinfo, series=series)
