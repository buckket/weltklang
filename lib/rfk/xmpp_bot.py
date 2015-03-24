import ast
import sys
import logging

import click

import zmq

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import XMPPError

import rfk
from rfk.helper import get_path
import rfk.helper.daemonize


class RfKBot(ClientXMPP):

    def __init__(self, jid, password):
        super(RfKBot, self).__init__(jid, password)

        self.add_event_handler('session_start', self.start)

        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0060')  # Publish-Subscribe
        self.register_plugin('xep_0115')  # Entity Capabilities
        self.register_plugin('xep_0118')  # User Tune
        self.register_plugin('xep_0128')  # Service Discovery Extensions
        self.register_plugin('xep_0163')  # Personal Eventing Protocol
        self.register_plugin('xep_0199')  # XMPP Ping

        self.auto_authorize = True
        self.auto_subscribe = True

    def start(self, event):
        self.send_presence()
        self.get_roster()
        self['xep_0115'].update_caps()

    def send_messages(self, data):
        try:
            for recipient in data['recipients']:
                logging.info('Sending message to {}'.format(recipient))
                self.send_message(recipient, data['message'])
            return True
        except (KeyError, XMPPError):
            return False

    def update_tune(self, data):
        try:
            if data['tune']:
                (artist, title) = (data['tune']['artist'], data['tune']['title'])
                logging.info('Updating tune: {} - {}'.format(artist, title))
                self['xep_0118'].publish_tune(artist=artist, title=title)
            else:
                logging.info('Updating tune: None')
                self['xep_0118'].stop()
            return True
        except (KeyError, XMPPError):
            return False


@click.command()
@click.option('-j', '--jid', help='JID to use')
@click.option('-p', '--password', help='password to use', hide_input=True)
@click.option('-f', '--foreground', help='run in foreground', is_flag=True, default=False)
def main(jid, password, foreground):
    rfk.init(enable_geoip=False)
    if not jid:
        jid = rfk.CONFIG.get('xmpp', 'jid')
    if not password:
        password = rfk.CONFIG.get('xmpp', 'password')
    if not foreground:
        rfk.helper.daemonize.createDaemon(get_path())

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')

    # Setup XMPP instance
    xmpp = RfKBot(jid, password)

    # Connect to the XMPP server and start processing XMPP stanzas
    if xmpp.connect():
        xmpp.process(block=False)

        def message_handler(message):
            if message and message['type'] == 'message':
                data = ast.literal_eval(message['data'])
                try:
                    if data['type'] == 'message':
                        xmpp.send_messages(data)
                    elif data['type'] == 'tune':
                        xmpp.update_tune(data)
                except (KeyError, TypeError) as err:
                    logging.error('message_handler error: {}'.format(err))

        try:
            redis_client = StrictRedis(host='localhost', port=6379, decode_responses=True)
            redis_pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
            redis_pubsub.subscribe('rfk-xmpp')
            for message in redis_pubsub.listen():
                message_handler(message)
        except (ConnectionError, KeyboardInterrupt):
            xmpp.disconnect(wait=True)
            return False

    else:
        return False


if __name__ == '__main__':
    sys.exit(main())
