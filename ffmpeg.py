from structs import VideoMetadata, AudioStream, SubtitleStream
import subprocess
import json


def get_video_metadata(path):
    command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', path]
    result = subprocess.check_output(command)
    data = json.loads(result.decode('utf-8'))

    result = VideoMetadata()
    result.container = data['format']['format_name']
    result.container_long = data['format']['format_long_name']
    result.length = int(float(data['format']['duration']))
    result.bitrate = int(float(data['format']['bit_rate']))

    for stream in data['streams']:
        if stream['codec_type'] == 'video':
            result.video.codec = stream['codec_name']
            result.video.codec_long = stream['codec_long_name']
            result.video.bitrate = int(float(stream['bit_rate']))
            result.video.width = int(stream['width'])
            result.video.height = int(stream['height'])

        if stream['codec_type'] == 'audio':
            audio = AudioStream()
            audio.codec = stream['codec_name']
            audio.codec_long = stream['codec_long_name']
            audio.channels = int(stream['channels'])
            audio.bitrate = int(float(stream['bit_rate']))
            if 'language' in stream['tags']:
                audio.language = stream['tags']['language']
            if 'title' in stream['tags']:
                audio.title = stream['tags']['title']
            result.audio.append(audio)

        if stream['codec_type'] == 'subtitle':
            sub = SubtitleStream()
            sub.codec = stream['codec_name']
            sub.codec_long = stream['codec_long_name']
            if 'language' in stream['tags']:
                sub.language = stream['tags']['language']
            if 'title' in stream['tags']:
                sub.title = stream['tags']['title']
            result.subtitles.append(sub)

    return result
