class VideoMetadata:
    def __init__(self):
        self.container = None
        self.container_long = None
        self.video = VideoStream()
        self.audio = []
        self.subtitles = []
        self.length = 0
        self.bitrate = 0

    def get_human(self):
        return "{}/{}".format(self.video.get_name(), self.audio[0].get_name())

    def __repr__(self):
        return '<VideoMetaData {}>'.format(self.get_human())


class AudioStream:
    def __init__(self):
        self.codec = None
        self.codec_long = None
        self.language = None
        self.title = None
        self.channels = 2
        self.bitrate = 0

    def get_name(self):
        lookup = {
            "aac": "AAC",
            "ac3": "AC-3",
            "eac3": "E-AC-3"
        }
        if self.codec in lookup:
            return lookup[self.codec]
        else:
            return self.codec.capitalize()

    def __repr__(self):
        return '<AudioStream {} {} ({})>'.format(self.codec, self.language, self.title)


class VideoStream:
    def __init__(self):
        self.codec = None
        self.codec_long = None
        self.bitrate = 0
        self.width = 0
        self.height = 0

    def get_name(self):
        lookup = {
            "hevc": "HEVC",
            "h264": "H.264"
        }
        if self.codec in lookup:
            return lookup[self.codec]
        else:
            return self.codec.capitalize()


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
