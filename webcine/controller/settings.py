from flask import render_template

from webcine.app import app
from webcine.models import User
from webcine.utils.auth import auth


@app.route('/admin/users')
@auth.admin_required
def admin_users():
    users = list(User.select())
    return render_template('settings/users.html', users=users)
