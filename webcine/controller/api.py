from flask import request

from webcine.app import app
from webcine.utils import transcoder


@app.route('/mark-transcode-progress/<int:transcode_id>/<int:progress>')
def mark_transcode_progress(transcode_id, progress):
    transcoder.progress_transcode_task(transcode_id, progress)
    return '{}'


@app.route('/mark-transcode-done/<int:id>/<float:speedfactor>')
def mark_transcode_done(id, speedfactor):
    transcoder.finished_transcode_task(id, speedfactor)
    return '{}'


@app.route('/mark-transcode-fail/<int:id>')
def mark_transcode_fail(id):
    transcoder.failed_transcode_task(id)
    return '{}'


@app.route('/transcode-callback', methods=['POST'])
def transcode_callback():
    data = request.get_json()
    id = int(data['id'])
    if data['status'] == 'started':
        transcoder.progress_transcode_task(id, 1)
    elif data['status'] == 'running':
        transcoder.progress_transcode_task(id, data['progress'])
    elif data['status'] == 'done':
        transcoder.finished_transcode_task(id, 0)
    return 'OK'
