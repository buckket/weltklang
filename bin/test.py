'''
Created on 04.05.2012

@author: teddydestodes
'''
import rfk
import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rfk.config.read(os.path.join(current_dir,'etc','config.cfg'))

    engine = create_engine("%s://%s:%s@%s/%s?charset=utf8" % (rfk.config.get('database', 'engine'),
                                                              rfk.config.get('database', 'username'),
                                                              rfk.config.get('database', 'password'),
                                                              #rfk.config.get('database', 'host'),
                                                              '192.168.2.101',
                                                              rfk.config.get('database', 'database')), echo=True)
    
    
    rfk.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    user = session.query(rfk.User).get(124)
    shows = rfk.Show.getCurrentShows(session, user)
    
    currshow = None
    print shows
    for show in shows:
        if currshow and show.end is None:
            print show.show
            show.end = datetime.today()
            break
        currshow = show
    print currshow.show
    
    
    """show = session.query(rfk.Show).get(180)
    
    tags = 'penisrock pop post.rock schwarzmetall black.metal'
    
    
    show.updateTags(session,tags)
    """
    """
    user = session.query(rfk.User).filter(rfk.User.name == 'teddydestodes').first()
    print rfk.Show.getCurrentShows(session, user)
    session.commit()
    """