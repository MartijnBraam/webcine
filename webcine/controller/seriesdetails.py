from flask import request, redirect, url_for, render_template, send_file, Response

from webcine.app import app
from webcine.models import WatchInfo, Media, Series, Actor, SeriesActor, Season
from webcine.utils.auth import auth


@app.route('/series-details/<int:series_id>')
@auth.login_required
def series_details(series_id):
    user = auth.get_logged_in_user()
    series = Series.get(Series.id == series_id)
    seasons = Season.select().where(Season.series == series)
    episodes = list(Media.select().where(Media.series == series).order_by(-Media.season, -Media.episode))
    season_episodes = {}
    for episode in episodes:
        if episode.season not in season_episodes.keys():
            season_episodes[episode.season] = {}
        season_episodes[episode.season][episode.episode] = episode
    actors = SeriesActor.select().join(Actor).where(SeriesActor.series == series)
    return render_template('series-details.html', series=series, season_episodes=season_episodes, actors=actors,
                           seasons=seasons)


@app.route('/mark-season-watched/<int:season_id>')
@auth.login_required
def mark_season_watched(season_id):
    """ This function does horrible things to your mysql. (n*2)+3 queries"""
    user = auth.get_logged_in_user()
    season = Season.get(Season.id == season_id)
    episodes = list(Media.select().where((Media.series == season.series) & (Media.season == season.number)))
    for episode in episodes:
        info = WatchInfo().get((WatchInfo.user == user) & (WatchInfo.media == episode))
        info.watched = True
        info.save()

    return redirect(url_for('homepage'))
