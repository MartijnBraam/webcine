import pika
import argparse
import json
import ffmpeg
import requests
import os

task_id = None


def progress_callback(progress):
    requests.get('http://{}/mark-transcode-progress/{}/{}'.format(args.host, task_id, progress))


def transcode(ch, method, properties, body):
    global task_id
    body = json.loads(body.decode())
    if body['codec'] == 'x264':
        parameters = {
            'path': os.path.join(args.storagepath, body['file']),
            'target': os.path.join(args.storagepath, body['target'])
        }
        if 'crf' in body:
            parameters['crf'] = body['crf']
        if 'max_bitrate' in body:
            parameters['max_bitrate'] = body['max_bitrate']
        if 'tune' in body:
            parameters['tune'] = body['tune']
        parameters['progress_callback'] = progress_callback
        task_id = body['id']
        ffmpeg.transcode_x264(**parameters)
        requests.get('http://{}/mark-transcode-done/{}'.format(args.host, body['id']))
        ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Webcine transcoding daemon")
    parser.add_argument('--host', help='RabbitMQ hostname', default='localhost')
    parser.add_argument('storagepath', help='Path to storage root')

    args = parser.parse_args()

    connection = pika.BlockingConnection(pika.ConnectionParameters(args.host, heartbeat_interval=0))
    channel = connection.channel()
    channel.queue_declare(queue='transcode', durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(transcode, queue='transcode')
    channel.start_consuming()
