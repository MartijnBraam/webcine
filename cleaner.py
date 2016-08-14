from models import Media
import ffmpeg


def remove_broken_media():
    """ Remove unplayable media files (video files containing no video data at all) """
    for media in Media.select().where(Media.length >> None):
        try:
            probe = ffmpeg.get_video_metadata(media.path)
            media.length = probe.length
            media.save()
        except:
            media.delete_instance(recursive=True)
