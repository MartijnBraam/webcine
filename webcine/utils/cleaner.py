from webcine.models import Media
from webcine.utils import ffmpeg
import logging


def remove_broken_media():
    """ Remove unplayable media files (video files containing no video data at all) """
    for media in Media.select().where(Media.length >> None):
        try:
            logging.info('Processing file {}'.format(media.path))
            probe = ffmpeg.get_video_metadata(media.path)
            media.length = probe.length
            media.save()
        except:
            media.delete_instance(recursive=True)
