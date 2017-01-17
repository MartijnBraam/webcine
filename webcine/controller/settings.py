from flask import render_template, request

from webcine.app import app
from webcine.models import User
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
    entity.enabled = payload['enabled']

    if payload['password'] != "":
        entity.set_password(payload['password'])

    entity.save()
    return '{}'
