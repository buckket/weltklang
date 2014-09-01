import sys
import ast

import click

import redis
import redis.exceptions

import rfk
import rfk.database
from rfk.database.show import Show
from rfk.database.track import Track

from rfk.helper import get_path
import rfk.helper.daemonize


redis_client = None


class XMPP(object):
    channel = 'rfk-xmpp'

    @staticmethod
    def send_messages(recipients, message):
        payload = {'recipients': recipients, 'message': message, 'type': 'message'}
        redis_client.publish(XMPP.channel, payload)

    @staticmethod
    def update_tune(artist=None, title=None):
        if artist and title:
            payload = {'type': 'tune', 'tune': {'artist': artist, 'title': title}}
        else:
            payload = {'type': 'tune', 'tune': None}
        redis_client.publish(XMPP.channel, payload)


class PushProwl(object):
    @staticmethod
    def send_messages(recipients, message):
        pass


class PushAndroid(object):
    @staticmethod
    def send_messages(recipients, message):
        pass


def handle_track_change(track_id):
    # track changed
    if track_id:
        track = Track.query.filter(Track.track == track_id).first()
        if track:
            XMPP.update_tune(artist=track.title.artist.name, title=track.title.name)
    # DJ disconnected -> no more tracks
    else:
        XMPP.update_tune()


def handle_show_change(show_id):
    # show changed
    if show_id:
        show = Show.query.filter(Show.show == show_id).first()
        if show:
            message = u"{} just started streaming {}".format(show.get_active_user().username, show.name)
            XMPP.send_messages(['buckket@jabber.ccc.de'], message)
    # show stopped
    else:
        pass

@click.command()
@click.option('-f', '--foreground', help='run in foreground', is_flag=True, default=False)
def main(foreground):
    if not foreground:
        rfk.helper.daemonize.createDaemon(get_path())

    rfk.init()
    rfk.database.init_db("%s://%s:%s@%s/%s" % (rfk.CONFIG.get('database', 'engine'),
                                               rfk.CONFIG.get('database', 'username'),
                                               rfk.CONFIG.get('database', 'password'),
                                               rfk.CONFIG.get('database', 'host'),
                                               rfk.CONFIG.get('database', 'database')))

    global redis_client
    redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True)
    pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('rfk-event')

    try:
        for message in pubsub.listen():
            if message and message['type'] == 'message':
                data = ast.literal_eval(message['data'])
                try:
                    if data['event'] == 'show_change':
                        handle_show_change(data['show_id'])
                    elif data['event'] == 'track_change':
                        handle_track_change(data['track_id'])
                except (KeyError, TypeError):
                    pass
    except KeyboardInterrupt:
        return False


if __name__ == '__main__':
    sys.exit(main())
