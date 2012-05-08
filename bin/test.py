'''
Created on 04.05.2012

@author: teddydestodes
'''
import rfk
import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rfk.config.read(os.path.join(current_dir,'etc','config.cfg'))

    engine = create_engine("%s://%s:%s@%s/%s?charset=utf8" % (rfk.config.get('database', 'engine'),
                                                              rfk.config.get('database', 'username'),
                                                              rfk.config.get('database', 'password'),
                                                              rfk.config.get('database', 'host'),
                                                              rfk.config.get('database', 'database')), echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    toptitles = rfk.Title.getTopTitles(session)
    print '----'
    for title,count in toptitles:
        print "%d %s - %s" % (count, title.name, title.artist.name)
        
    print '----'
    topartists = rfk.Artist.getTopArtists(session)
    for artist,count in topartists:
        print "%d %s" % (count, artist.name)
    print '----'
    topusers = rfk.User.getTopUserByShow(session)
    
    for user, count in topusers:
        print "%d %s" % (count, user.name)
    
    topusers = rfk.User.getTopUserByShowLength(session)
    print '----'
    for user, time in topusers:
        print "%d %d %s" % (time.days, time.seconds, user.name)
        