from flask import render_template, request, redirect, url_for

from webcine.app import app
from webcine.models import User, TranscodedMedia, Media, TranscodingSettings
from webcine.utils.auth import auth


@app.route('/status')
@auth.admin_required
def admin_users():
    transcoding = TranscodedMedia.select().join(Media).join(TranscodingSettings)
    return render_template('status/transcoder.html', transcoding=transcoding)