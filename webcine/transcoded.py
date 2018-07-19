import argparse
import json
import os
import sys

import requests

from webcine.utils import ffmpeg
from webcine.utils import queue

task_id = None


def progress_callback(progress):
    requests.get('http://{}/mark-transcode-progress/{}/{}'.format(args.host, task_id, progress))


def transcode(ch, method, properties, body):
    global task_id
    print('Got transcode task')
    body = json.loads(body.decode())
    if body['codec'] == 'x264':
        print('   codec: x264')
        parameters = {
            'path': os.path.join(args.storagepath, body['file']),
            'target': os.path.join(args.storagepath, body['target'])
        }
        print('    source: {path}\n    target: {target}'.format(**parameters))
        if 'crf' in body:
            parameters['crf'] = body['crf']
        if 'max_bitrate' in body:
            parameters['max_bitrate'] = body['max_bitrate']
        if 'tune' in body:
            parameters['tune'] = body['tune']
        parameters['progress_callback'] = progress_callback
        task_id = body['id']
        print('    start transcode')
        try:
            speedfactor = ffmpeg.transcode_x264(**parameters)
            requests.get('http://{}/mark-transcode-done/{}/{}'.format(args.host, body['id'], speedfactor))
            print('    finished transcode')
        except:
            requests.get('http://{}/mark-transcode-fail/{}'.format(args.host, body['id']))
            print('    transcode failed')
        ch.basic_ack(delivery_tag=method.delivery_tag)


def validate_storage_root(path):
    if not os.path.isdir(path):
        print('Storage path {} is not an existing directory'.format(path), file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Webcine transcoding daemon")
    parser.add_argument('--queue', help='AMQP Server url', default='amqp://localhost')
    parser.add_argument('--host', help='Webcine host', default='localhost')
    parser.add_argument('storagepath', help='Path to storage root')

    args = parser.parse_args()

    validate_storage_root(args.storagepath)

    connection = queue.create_connection_from_url(args.queue)
    channel = connection.channel()
    channel.queue_declare(queue='transcode', durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(transcode, queue='transcode')
    print('Start listening for transcode tasks')
    channel.start_consuming()
