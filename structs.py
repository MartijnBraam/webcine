class VideoMetadata:
    def __init__(self):
        self.container = None
        self.container_long = None
        self.video = VideoStream()
        self.audio = []
        self.subtitles = []
        self.length = 0
        self.bitrate = 0


class AudioStream:
    def __init__(self):
        self.codec = None
        self.codec_long = None
        self.language = None
        self.title = None
        self.channels = 2
        self.bitrate = 0

    def __repr__(self):
        return '<AudioStream {} {} ({})>'.format(self.codec, self.language, self.title)


class VideoStream:
    def __init__(self):
        self.codec = None
        self.codec_long = None
        self.bitrate = 0
        self.width = 0
        self.height = 0


class SubtitleStream:
    def __init__(self):
        self.codec = None
        self.codec_long = None
        self.language = None
        self.title = None


class EpisodeInfo:
    def __init__(self):
        self.episode_title = None
        self.series_name = None
        self.episode_number = 0
        self.season_number = 0
        self.description = None
        self.thumbnail = None
        self.actors = []


class ActorInfo:
    def __init__(self):
        self.name = None
        self.role = None
        self.picture = None
