from flask import Response
from werkzeug.contrib.atom import AtomFeed
from rfk.feeds import feeds, get_shows


@feeds.route('/atom')
def atom():
        
    # init feed
    feed = AtomFeed('Radio freies Krautchen', subtitle='Upcomming shows', url='http://radio.krautchan.net')

    # adding planned shows
    result = get_shows()
    
    if result:
        for show in result:
            feed.add(id=str(show.show),
                     title=show.name,
                     content=show.description,
                     author='dj',
                     url='http://krautchan.net',
                     updated=show.begin,
                     published=show.begin)
            
    return feed.get_response()
