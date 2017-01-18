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
* rabbitmq server
* webserver to handle static file serving and wsgi (apache, nginx)

## Screenshots

![Dashboard](http://brixitcdn.net/github/webcine/dashboard.png)
![Player](http://brixitcdn.net/github/webcine/player.png)

## Installation

```bash
$ git clone [this repo] /opt/webcine
$ apt install libapache2-mod-wsgi-py3 rabbitmq-server mysql-server
```

Configure mod_wsgi in apache (see `installation/apache-vhost.conf` as example)

Open the url defined in your apache vhost and login with admin/admin