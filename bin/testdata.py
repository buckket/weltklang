import os
import inspect
from pprint import pprint
import datetime
import rfk
import rfk.database
from rfk.database.base import User, News, ApiKey
from rfk.database.show import Show, Tag


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
    show.end = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    show.flags = Show.FLAGS.PLANNED
    shows.append(show)
    
    for show in shows:
        user = User.get_user(username='teddydestodes')
        show.add_user(user)
        user = User.get_user(username='MrLoom')
        show.add_user(user)
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


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rfk.init(current_dir)
    rfk.database.init_db("%s://%s:%s@%s/%s?charset=utf8" % (rfk.CONFIG.get('database', 'engine'),
                                                            rfk.CONFIG.get('database', 'username'),
                                                            rfk.CONFIG.get('database', 'password'),
                                                            rfk.CONFIG.get('database', 'host'),
                                                            rfk.CONFIG.get('database', 'database')))
    add_users()
    add_shows()
    add_news()
    add_apikey()
    