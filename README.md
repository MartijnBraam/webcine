# Webcine

A media center application build as a webapplication (like plex and netflix) written in python 3. 

## Features

* Full html5 based interface (no video player plugins)
* Ahead of time video transcoding for incompatible file formats
* Transcoding on other/multiple computers
* Sickbeard integration

## Roadmap

* Transmission / Sabnzbd / Couchpotato integration
* Mobile version
* Android TV version
* Theme support

## Requirements

* mysql server
* webserver to handle static file serving and wsgi (apache, nginx)
* Sickbeard if you want to add a tv library (It depends on sickbeard metadata)

## Screenshots

![Dashboard](http://brixitcdn.net/github/webcine/dashboard.png)
![Player](http://brixitcdn.net/github/webcine/player.png)

## Installation

```bash
$ git clone [this repo] /opt/webcine
$ apt install apache2 libapache2-mod-wsgi-py3 mysql-server
$ a2enmod wsgi
# This is for debian 9, flask_peewee is packaged in debian 10
$ apt install python3-pip python3-pymysql python3-tvdb-api python3-tmdbsimple python3-xmltodict
$ pip3 install flask_peewee

# Copy the configuration template
$ cp /opt/webcine/config.example.ini /etc/webcine.conf
```

Configure mod_wsgi in apache (see `installation/apache-vhost.conf` as example)

Open the url defined in your apache vhost and login with admin/admin