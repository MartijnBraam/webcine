from models import Library, Series, Actor, MediaActor, SeriesActor, Media, User, SeriesWatchInfo, WatchInfo
from glob import glob
import os
import tools
import xmltodict
import re
from app import celery
from ffmpeg import get_video_metadata
import logging

logging.basicConfig(level=logging.INFO)

REGEX_EPISODE = re.compile(r'(?:S(\d+)E(\d+)|[^0-9x](\d)(\d\d)[^0-9p])', re.IGNORECASE)
REGEX_VIDEOEXT = re.compile(r'(mp4|mkv|mpg|avi|wmv|ts)$', re.IGNORECASE)


def parse_episode_number(filename):
    try:
        match = REGEX_EPISODE.search(filename)
        if match:
            groups = match.groups()
            return int(groups[0]), int(groups[1])
        else:
            logging.error('No episode number in filename: {}'.format(filename))
            return None
    except Exception:
        logging.error('Cannot parse episode number in: {}'.format(filename))
        if groups:
            logging.error(groups)
        raise


def index_sickbeard(path, library):
    logging.info('Processing sickbeard index in {}'.format(path))
    for nfo_file in glob(path + '/*/tvshow.nfo'):
        with open(nfo_file) as handle:
            nfo = xmltodict.parse(handle.read())

        directory = nfo_file.replace('/tvshow.nfo', '')

        series, created = Series.create_or_get(tvdb_id=nfo['tvshow']['id'], name=nfo['tvshow']['title'])

        if created:
            logging.info('Added new series to index: {}'.format(nfo['tvshow']['title']))
        else:
            logging.info('Scanning existing show: {}'.format(nfo['tvshow']['title']))

        if created:
            series.description = nfo['tvshow']['plot']
            series.genre = nfo['tvshow']['genre']
            series.mpaa = nfo['tvshow']['mpaa']
            series.studio = nfo['tvshow']['studio']
            series.save()

            if os.path.isfile(directory + '/poster.jpg'):
                logging.info('Added poster.jpg from series directory')
                tools.cache_image_from_library(directory + '/poster.jpg', 'series', series.id)

            if isinstance(nfo['tvshow']['actor'], dict):
                nfo['tvshow']['actor'] = [nfo['tvshow']['actor']]
            for show_actor in nfo['tvshow']['actor']:
                actor, created = Actor.create_or_get(name=show_actor['name'])
                logging.info('Processing actor {}'.format(show_actor['name']))
                if created and 'thumb' in show_actor and show_actor['thumb'] is not None:
                    tools.cache_image(show_actor['thumb'], 'actor', actor.id)
                SeriesActor.create(series=series, actor=actor, personage=show_actor['role'])

            for user in User.select():
                logging.info('Adding WatchInfo for user {}'.format(user.username))
                SeriesWatchInfo.create(user=user, series=series).save()

        for season in glob(directory + '/Season */'):
            for episode in glob(season + '*'):
                test = REGEX_VIDEOEXT.search(episode)
                if test:
                    logging.info('Processing episode file')
                    season_number, episode_number = parse_episode_number(episode)
                    logging.info('Episode file is season {} episode {}'.format(season_number, episode_number))
                    try:
                        Media.get(Media.series == series and Media.episode == episode_number and
                                  Media.season == season_number)
                    except:
                        logging.info('Episode file not indexed yet. Indexing now')
                        media = Media()
                        media.type = 'tvepisode'
                        media.library = library
                        media.series = series
                        media.season = season_number
                        media.episode = episode_number
                        media.path = episode
                        media.name = '[processing...]'
                        media.save()

                        logging.info('Creating ffprobe task for backgroundworker')
                        preprocess_media_file.delay(media.id)

                        episode_thumb = os.path.splitext(episode)[0] + '.thumb.jpg'
                        if os.path.isfile(episode_thumb):
                            logging.info('Using episode thumbnail from season folder')
                            tools.cache_image_from_library(episode_thumb, 'media', media.id)
                        episode_nfo = os.path.splitext(episode)[0] + '.nfo'
                        if os.path.isfile(episode_nfo):
                            logging.info('Processing episode .nfo file')
                            with open(episode_nfo) as handle:
                                episode_nfo = xmltodict.parse(handle.read())
                            media.name = episode_nfo['episodedetails']['title']
                            media.description = episode_nfo['episodedetails']['plot']
                            if 'thumb' in episode_nfo['episodedetails'] and episode_nfo['episodedetails'][
                                'thumb'] is not None:
                                logging.info('Downloading thumbnail from episode .nfo file')
                                tools.cache_image(episode_nfo['episodedetails']['thumb'], 'media_thumb', media.id)

                            media.save()

                            if isinstance(episode_nfo['episodedetails']['actor'], dict):
                                episode_nfo['episodedetails']['actor'] = [episode_nfo['episodedetails']['actor']]

                            for show_actor in episode_nfo['episodedetails']['actor']:
                                if 'thumb' in show_actor and 'role' in show_actor:
                                    actor, created = Actor.create_or_get(name=show_actor['name'])
                                    if created and 'thumb' in show_actor and show_actor['thumb'] is not None:
                                        tools.cache_image(show_actor['thumb'], 'actor', actor.id)
                                    MediaActor.create(media=media, actor=actor, personage=show_actor['role'])


@celery.task
def preprocess_media_file(media_id):
    logging.info('Running ffprobe on media {}'.format(media_id))
    media = Media.get(Media.id == media_id)
    metadata = get_video_metadata(media.path)
    media.length = metadata.length
    media.save()
    return True


def index():
    for library in list(Library.select()):
        path = 'storage/{}'.format(library.name)
        if library.type == 'tvseries':
            if library.structure == 'sickbeard':
                index_sickbeard(path, library)
