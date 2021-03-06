import logging
import subprocess
from glob import glob

import os
import re
import tmdbsimple as tmdb
import xmltodict
from webcine.app import app
from webcine.models import Library, Series, Actor, MediaActor, SeriesActor, Media, User, SeriesWatchInfo, WatchInfo
from webcine.structs import EpisodeInfo, ActorInfo
from webcine.utils import tools
from webcine.utils.ffmpeg import get_video_metadata
from webcine.utils.nameparser import parse_episode_number

REGEX_VIDEOEXT = re.compile(r'(mp4|mkv|mpg|avi|wmv|ts)$', re.IGNORECASE)
REGEX_MOVIE_DIRECTORY = re.compile(r'(.+)\((\d{4})\)')

tmdb.API_KEY = '329e421f927379309e3631719b6d42b3'


def load_xbmc_episode_metadata(filename):
    logging.info('Processing xbmc metadata {}'.format(filename))
    with open(filename) as handle:
        xml_data = handle.read()
    episode_nfo = xmltodict.parse(xml_data)
    episodes = []
    if 'xbmcmultiepisode' in episode_nfo:
        episodes.extend(episode_nfo['xbmcmultiepisode']['episodedetails'])
    else:
        episodes.append(episode_nfo['episodedetails'])
    result = []
    for episode in episodes:
        if isinstance(episode['actor'], dict):
            episode['actor'] = [episode['actor']]

        processed = EpisodeInfo()
        processed.episode_title = episode['title']
        processed.series_name = episode['showtitle']
        processed.season_number = int(episode['season'])
        processed.episode_number = int(episode['episode'])
        processed.description = episode['plot']

        if 'thumb' in episode and episode['thumb']:
            processed.thumbnail = episode['thumb']

        for actor in episode['actor']:
            ai = ActorInfo()
            ai.name = actor['name']
            if 'role' in actor:
                ai.role = actor['role']
            if 'thumb' in actor:
                ai.picture = actor['thumb']
            processed.actors.append(ai)

        result.append(processed)
    return result


def index_sickbeard_season(path, library, series):
    for episode in glob(path + '*'):
        test = REGEX_VIDEOEXT.search(episode)
        if test and not '.sample.' in episode:
            logging.info('Processing episode file')
            season_number, episode_number = parse_episode_number(episode)
            logging.info('Episode file is season {} episode {}'.format(season_number, episode_number))
            try:
                Media.get(Media.series == series, Media.episode == episode_number,
                          Media.season == season_number)
            except Media.DoesNotExist:
                print('New episode: {} S{} E{}'.format(series.name, season_number, episode_number))
                media = Media()
                media.type = 'tvepisode'
                media.library = library
                media.series = series
                media.season = season_number
                media.episode = episode_number
                media.path = episode.replace(app.config['STORAGE'] + '/', '')
                media.name = '[processing...]'
                media.save()

                logging.info('Creating ffprobe task for backgroundworker')
                preprocess_media_file(media.id)

                episode_thumb = os.path.splitext(episode)[0] + '.thumb.jpg'
                if os.path.isfile(episode_thumb):
                    logging.info('Using episode thumbnail from season folder')
                    tools.cache_image_from_library(episode_thumb, 'media', media.id)
                episode_nfo = os.path.splitext(episode)[0] + '.nfo'
                if os.path.isfile(episode_nfo):
                    logging.info('Processing episode .nfo file')
                    episode_nfo = load_xbmc_episode_metadata(episode_nfo)

                    media.name = episode_nfo[0].episode_title
                    media.description = episode_nfo[0].description

                    if len(episode_nfo) > 1:
                        media.dual_episode = True

                    if episode_nfo[0].thumbnail is not None:
                        logging.info('Downloading thumbnail from episode .nfo file')
                        tools.cache_image(episode_nfo[0].thumbnail, 'media_thumb', media.id)

                    media.save()

                    for swi in SeriesWatchInfo.select().where(SeriesWatchInfo.following == True,
                                                              SeriesWatchInfo.series == series):
                        WatchInfo.create(user=swi.user, media=media)

                    for show_actor in episode_nfo[0].actors:
                        actor, created = Actor.create_or_get(name=show_actor.name)
                        if created and show_actor.picture is not None:
                            tools.cache_image(show_actor.picture, 'actor', actor.id)

                        media_actor = MediaActor.create(media=media, actor=actor)
                        if show_actor.role:
                            media_actor.personage = show_actor.role
                            media_actor.save()
                else:
                    print("Missing metadata file: {}".format(episode_nfo))


def index_sickbeard(path, library):
    logging.info('Processing sickbeard index in {}'.format(path))
    for nfo_file in glob(path + '/*/tvshow.nfo'):
        logging.info('Processing {}'.format(nfo_file))
        with open(nfo_file) as handle:
            xml_data = handle.read()
        nfo = xmltodict.parse(xml_data)

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
            index_sickbeard_season(season, library, series)


def get_largest_file(directory):
    largest_size = 0
    largest_file = None
    for file in glob(os.path.join(directory, '*')):
        size = os.path.getsize(file)
        if size > largest_size:
            largest_size = size
            largest_file = file
    return largest_file


def add_media_watchinfo(media_id):
    for user in User.select():
        logging.info('Adding WatchInfo for user {}'.format(user.username))
        media = Media.get(Media.id == media_id)
        WatchInfo.create(user=user, media=media).save()


def index_movie(path, library, name, year):
    movie_file = get_largest_file(path)
    if not movie_file:
        print("  No movie found in directory")
        return
    try:
        probe = get_video_metadata(movie_file, is_absolute_path=True)
    except Exception as e:
        print("  Media probe failed on {}".format(movie_file))
        print(e)
        return
    try:
        Media.get(Media.path == movie_file)
    except:
        print("Adding movie {} ({}) to index".format(name, year))
        ts = tmdb.Search()
        logging.info('Querying tmdb for movie info')
        result = ts.movie(query=name, year=year)
        if len(result['results']) == 0:
            result = ts.movie(query=name)
        if len(result['results']) == 0:
            logging.error('Cannot find {} ({}) on themoviedb.org'.format(name, year))
            return
        result = result['results'][0]

        media = Media()
        media.description = result['overview']
        media.type = 'movie'
        media.length = probe.length
        media.codec = probe.get_human()
        media.library = library
        media.path = movie_file
        media.name = name
        media.bitrate = probe.bitrate
        media.save()

        print("Downloading poster")
        poster_path = result['poster_path']
        poster_url = 'http://image.tmdb.org/t/p/w500{}'.format(poster_path)
        tools.cache_image(poster_url, 'movie', media.id)
        add_media_watchinfo(media.id)


def index_movie_directory(path, library):
    logging.info('Processing movie index in {}'.format(path))
    for movie in glob(path + '/*'):
        parsed = REGEX_MOVIE_DIRECTORY.search(os.path.basename(movie))
        if parsed:
            name, year = parsed.groups()
            year = int(year)
            name = name.strip()
            print("Indexing {} ({})".format(name, year))
            index_movie(movie, library, name, year)


def preprocess_media_file(media_id):
    logging.info('Running ffprobe on media {}'.format(media_id))
    media = Media.get(Media.id == media_id)
    try:
        metadata = get_video_metadata(media.path)
        media.length = metadata.length
        media.codec = metadata.get_human()
        media.bitrate = metadata.bitrate
    except subprocess.CalledProcessError as e:
        media.playable = False
    media.save()
    return True


def reprobe_for_missing_codec_data():
    for media in Media.select().where((Media.bitrate >> None) | (Media.codec >> None) | (Media.length >> None)):
        try:
            metadata = get_video_metadata(media.path)
        except:
            media.delete_instance(recursive=True)
            continue
        media.bitrate = metadata.bitrate
        media.codec = metadata.get_human()
        media.length = metadata.length
        media.save()


def index():
    for library in list(Library.select()):
        path = '{}/{}'.format(app.config['STORAGE'], library.name)
        logging.info('Running indexer for {} library'.format(library.name))
        if library.type == 'tvseries':
            logging.info('Library format is tv series')
            if library.structure == 'sickbeard':
                print("Indexing {}".format(path, library.name))
                logging.info('Library format is Sickbeard/Sickrage')
                index_sickbeard(path, library)
        if library.type == 'movies':
            logging.info('Library format is movies')
            if library.structure == 'couchpotato':
                print("Indexing {}".format(path, library.name))
                logging.info('Library format is Couchpotato')
                index_movie_directory(path, library)
