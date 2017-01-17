from flask import render_template, request

from webcine.app import app
from webcine.models import User
import webcine.models
from webcine.utils.auth import auth


@app.route('/admin/users')
@auth.admin_required
def admin_users():
    users = list(User.select())
    return render_template('settings/users.html', users=users)


@app.route('/admin/save/<entity>', methods=['POST'])
@auth.admin_required
def admin_save_entity(entity):
    entity = entity.title()
    payload = request.json
    entity = getattr(webcine.models, entity).get(getattr(webcine.models, entity).id == payload['id'])
    return repr(entity)
