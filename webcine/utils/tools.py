import requests
import os
import shutil


def format_resolution(width, height):
    if height > width:
        height, width = width, height

    if height < 720:
        return 'SD'
    if width == 1280:
        return '720p'
    if width == 1920:
        return '1080p'
    if 719 < height < 1081:
        return 'HD'
    if 1920 < width < 4095:
        return '2K'
    return '4K'


def cache_image(url, type, id, ext='jpg'):
    response = requests.get(url)
    path = 'storage/cache/{}/{}.{}'.format(type, id, ext)

    if not os.path.isdir('storage/cache/{}'.format(type)):
        os.mkdir('storage/cache/{}'.format(type))

    with open(path, 'wb') as handle:
        handle.write(response.content)


def cache_image_from_library(path, type, id):
    name, ext = os.path.splitext(path)
    if not os.path.isdir('storage/cache/{}'.format(type)):
        os.mkdir('storage/cache/{}'.format(type))

    shutil.copy(path, 'storage/cache/{}/{}{}'.format(type, id, ext))
