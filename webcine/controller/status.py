from flask import render_template, request, redirect, url_for

from webcine.app import app, db
from webcine.models import User, TranscodedMedia, Media, TranscodingSettings
from webcine.utils.auth import auth


@app.route('/status')
@auth.admin_required
def transcoder_status():
    sql = """SELECT
      transcodedmedia.id,
      done,
      progress,
      speedfactor,
      media.codec               AS input_codec,
      media.bitrate             AS input_bitrate,
      transcodingsettings.codec AS output_codec
    FROM transcodedmedia, media, transcodingsettings
    WHERE transcodedmedia.media_id = media.id
          AND transcodingsettings.id = transcodedmedia.settings_id
    """

    cursor = db.database.execute_sql()
    transcoding = list(cursor.fetchall())
    return render_template('status/transcoder.html', transcoding=transcoding)
