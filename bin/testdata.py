import os
import inspect
from pprint import pprint
import datetime
import rfk
import rfk.database
from rfk.database.base import User, News, ApiKey, Setting
from rfk.database.show import Show, Tag
from rfk.database.track import Track
from rfk.database.streaming import Stream, Relay


def add_users():
    users = []
    users.append(User.add_user('mrloom', 'mrluhm'))
    users.append(User.add_user('teddydestodes', 'drama'))
    for user in users:
        rfk.database.session.add(user)
        print "[users] Added %s" % user.username
    rfk.database.session.commit()
    
def add_shows():
    shows = []
    
    show = Show(name='Testsendung #1', description='Testbeschreibung')
    show.begin = datetime.datetime.utcnow()
    show.end = None
    show.flags = Show.FLAGS.UNPLANNED
    shows.append(show)
    
    show = Show(name='Testsendung #2', description='Hurf Durf')
    show.begin = datetime.datetime.utcnow()
    show.end = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    show.flags = Show.FLAGS.PLANNED
    shows.append(show)
    
    for show in shows:
        user = User.get_user(username='teddydestodes')
        show.add_user(user)
        rfk.database.session.commit()
        user = User.get_user(username='MrLoom')
        show.add_user(user)
        rfk.database.session.commit()
        tags = Tag.parse_tags('pups benis bagina')
        show.add_tags(tags=tags)
        rfk.database.session.commit()
        rfk.database.session.add(show)
        print "[shows] Added '%s' (%s)" % (show.name, show.description)
    rfk.database.session.commit()

def add_news():
    news = []
    news.append(News(user = User.get_user(username='MrLoom'), title='Hallo Welt', content='Hallo Loom'))
    news.append(News(user = User.get_user(username='teddydestodes'), title='Ich', content='ausversehen'))
    for newz in news:
        newz.time = datetime.datetime.utcnow()
        rfk.database.session.add(newz)
        print "[news] Added news from user %s" % newz.user
    rfk.database.session.commit()

def add_apikey():
    key = ApiKey(user = User.get_user(username='MrLoom'), application='Testo')
    key.gen_key()
    rfk.database.session.add(key)
    rfk.database.session.commit()
    print "[apikeys] Added key %s for user %s" % (key.key, key.user)

def add_tracks():
    show = Show.query.get(1)
    t = Track.new_track(show, "penis", "mann")
    rfk.database.session.add(t)
    rfk.database.session.commit()
    t = Track.new_track(show, "penis2", "mann")
    rfk.database.session.add(t)
    rfk.database.session.commit()
    t = Track.new_track(show, "penis2", "mann2")
    rfk.database.session.add(t)
    rfk.database.session.commit()
    t = Track.new_track(show, "penis", "mann2")
    rfk.database.session.add(t)
    rfk.database.session.commit()

def add_streams():
    stream = Stream()
    stream.mount = '/radio.ogg'
    stream.code = 'ogg'
    stream.name = 'Vorbis'
    stream.type = Stream.TYPES.OGG
    stream.quality = 3
    rfk.database.session.add(stream)
    stream = Stream()
    stream.mount = '/radiohq.ogg'
    stream.code = 'ogghq'
    stream.name = 'Vorbis HQ'
    stream.type = Stream.TYPES.OGG
    stream.quality = 6
    rfk.database.session.add(stream)
    stream = Stream()
    stream.mount = '/radio.mp3'
    stream.code = 'mp3'
    stream.name = 'MPEG Layer3'
    stream.type = Stream.TYPES.MP3
    stream.quality = 4
    rfk.database.session.add(stream)
    rfk.database.session.commit()


def add_relays():
    relay = Relay()
    relay.address = '192.168.122.222'
    relay.type = Relay.TYPE.MASTER
    relay.status = Relay.STATUS.UNKNOWN
    relay.port = 8000
    relay.admin_username = 'admin'
    relay.admin_password = 'entengruetze'
    relay.auth_username = 'master'
    relay.auth_password = 'master'
    relay.relay_password = 'radiowegrelayen'
    relay.relay_username = 'relay'
    rfk.database.session.add(relay)
    rfk.database.session.commit()

def add_settings():
    settings = []
    settings.append(Setting.add_setting('use_icy', 'Use ICY-Tags for unplanned Shows', Setting.TYPES.INT))
    settings.append(Setting.add_setting('show_def_name', 'Default Name for new Shows', Setting.TYPES.STR))
    settings.append(Setting.add_setting('show_def_desc', 'Default Description for new Shows', Setting.TYPES.STR))
    settings.append(Setting.add_setting('show_def_tags', 'Default Tags for new Shows', Setting.TYPES.STR))
    for setting in settings:
        rfk.database.session.add(setting)
    rfk.database.session.commit()    
    
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rfk.init(current_dir)
    rfk.database.init_db("%s://%s:%s@%s/%s?charset=utf8" % (rfk.CONFIG.get('database', 'engine'),
                                                            rfk.CONFIG.get('database', 'username'),
                                                            rfk.CONFIG.get('database', 'password'),
                                                            rfk.CONFIG.get('database', 'host'),
                                                            rfk.CONFIG.get('database', 'database')))
    add_settings()
    add_users()
    add_shows()
    add_tracks()
    add_streams()
    add_relays()
    add_news()
    add_apikey()
    
