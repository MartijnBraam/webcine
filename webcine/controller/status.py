from flask import render_template, request, redirect, url_for

from webcine.app import app, db
from webcine.models import User, TranscodedMedia, Media, TranscodingSettings
from webcine.utils.auth import auth


@app.route('/status')
@auth.admin_required
def transcoder_status():
    sql = """SELECT
      CONCAT(media.name, " (S", media.season," E", media.episode, ")"),
      done,
      progress,
      speedfactor,
      media.codec                           AS input_codec,
      round(media.bitrate / 1024 / 1024, 2) AS input_bitrate,
      transcodingsettings.codec             AS output_codec
    FROM transcodedmedia, media, transcodingsettings
    WHERE transcodedmedia.media_id = media.id
          AND transcodingsettings.id = transcodedmedia.settings_id
    """

    cursor = db.database.execute_sql(sql)
    transcoding = list(cursor.fetchall())
    return render_template('status/transcoder.html', transcoding=transcoding)
