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
