from flask import request, redirect, url_for, render_template, flash, send_file, Response
from app import app
from auth import auth
from models import User


@app.route('/admin/users')
@auth.admin_required
def admin_users():
    users = list(User.select())
    return render_template('settings/users.html', users=users)
