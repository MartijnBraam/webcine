import tvdb_api

from webcine.models import Series, Season


def update_tvdb_data():
    tvdb = tvdb_api.Tvdb()

    for series in Series.select():
        tvdb_series = tvdb[series.name]
        for season in tvdb_series:
            if season > 0:
                try:
                    Season.get(Season.series == series, Season.number == season)
                except:
                    print("Creating season info for {} season {}".format(series.name, season))
                    episodes = len(tvdb_series[season].keys())
                    Season.create(series=series, number=season, episodes=episodes)
