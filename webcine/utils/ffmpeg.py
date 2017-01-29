import json
import logging
import re
import subprocess
from webcine.utils.config import get_storage_path

from webcine.structs import VideoMetadata, AudioStream, SubtitleStream


def transcode_x264(path, target, crf=23, max_bitrate=None, tune='film', twopass=False, progress_callback=None):
    probe = get_video_metadata(path, True)

    command = ['ffmpeg', '-v', 'quiet', '-stats', '-y', '-i', path, '-c:v', 'libx264', '-crf', str(crf)]
    if max_bitrate:
        command.append('-maxrate')
        command.append('{}k'.format(max_bitrate * 1000))
    command.append('-tune')
    command.append(tune)
    command.append('-movflags')
    command.append('+faststart')
    command.append('-c:a')
    command.append('libfdk_aac')
    command.append('-b:a')
    audio_bitrate = probe.audio[0].channels * 64
    command.append('{}k'.format(audio_bitrate))

    command.append(target)
    return ffmpeg_wrapper(command, probe, progress_callback)


def ffmpeg_wrapper(command, metadata, progress_callback):
    total_time = metadata.length
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    regex_time = re.compile(r'time=(\d+:\d+:\d+)')
    last_progress = 0
    for line in process.stdout:
        time = regex_time.search(line)
        if time:
            time = time.groups()[0]
            hours, minutes, seconds = time.split(':')
            seconds = int(seconds)
            minutes = int(minutes)
            hours = int(hours)
            minutes += hours * 60
            seconds += minutes * 60
            progress = int((seconds / total_time) * 100.0)
            if progress > last_progress:
                print("Transcoding {}%".format(progress))
                last_progress = progress
                if progress_callback is not None:
                    progress_callback(progress)
    process.stdout.close()
    return process.wait()


def get_video_metadata(path, is_absolute_path=False):
    if not is_absolute_path:
        storage = get_storage_path()
        path = storage + '/' + path
    command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', path]
    result = subprocess.check_output(command)
    data = json.loads(result.decode('utf-8'))
    print(data)
    try:
        result = VideoMetadata()
        result.container = data['format']['format_name']
        result.container_long = data['format']['format_long_name']
        result.length = int(float(data['format']['duration']))
        result.bitrate = int(float(data['format']['bit_rate']))

        for stream in data['streams']:
            if stream['codec_type'] == 'video':
                result.video.codec = stream['codec_name']
                result.video.codec_long = stream['codec_long_name']
                if 'bit_rate' in stream:
                    result.video.bitrate = int(float(stream['bit_rate']))
                result.video.width = int(stream['width'])
                result.video.height = int(stream['height'])

            if stream['codec_type'] == 'audio':
                audio = AudioStream()
                audio.codec = stream['codec_name']
                audio.codec_long = stream['codec_long_name']
                audio.channels = int(stream['channels'])
                if 'bit_rate' in stream:
                    audio.bitrate = int(float(stream['bit_rate']))
                if 'tags' in stream:
                    if 'language' in stream['tags']:
                        audio.language = stream['tags']['language']
                    if 'title' in stream['tags']:
                        audio.title = stream['tags']['title']
                result.audio.append(audio)

            if stream['codec_type'] == 'subtitle':
                sub = SubtitleStream()
                sub.codec = stream['codec_name']
                sub.codec_long = stream['codec_long_name']
                if 'tags' in stream:
                    if 'language' in stream['tags']:
                        sub.language = stream['tags']['language']
                    if 'title' in stream['tags']:
                        sub.title = stream['tags']['title']
                result.subtitles.append(sub)
        print(result)
        return result
    except Exception as e:
        print('Exception in ffprobe process ({})'.format(path))
        print(data)
        logging.error('Exception in ffprobe process ({})'.format(path))
        logging.error(data)
        raise e
