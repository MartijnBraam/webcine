import pika
from urllib.parse import urlparse


def create_connection_from_url(url):
    host, port, vhost, credentials = _parse_amqp_url(url)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, port=port, virtual_host=vhost, credentials=credentials,
                                  heartbeat_interval=0))
    return connection


def _parse_amqp_url(url):
    if 'amqp://' not in url:
        url = 'amqp://' + url
    url = urlparse(url, 'amqp')
    host = url.hostname
    port = url.port if url.port else 5672
    vhost = url.path
    credentials = None

    if url.username:
        credentials = pika.PlainCredentials(url.username, url.password)

    return host, port, vhost, credentials
