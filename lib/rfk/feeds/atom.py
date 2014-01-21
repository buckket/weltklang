from flask import Response, url_for
from werkzeug.contrib.atom import AtomFeed
from rfk.feeds import feeds, get_shows, get_djs


@feeds.route('/atom')
def atom():
        
    # init feed
    feed = AtomFeed('Radio freies Krautchen', subtitle='Upcomming shows', url='http://radio.krautchan.net')

    # adding planned shows
    result = get_shows()
    
    if result:
        for show in result:
            
            djs = get_djs(show)
            author = ', '.join(djs)
            
            feed.add(id=str(show.show),
                     title=show.name,
                     content=show.description,
                     author=author,
                     url=url_for('show.show_view', show=show.show),
                     updated=show.begin,
                     published=show.begin)
    return feed.get_response()

