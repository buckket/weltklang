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
                                                              rfk.config.get('database', 'host'),
                                                              rfk.config.get('database', 'database')), echo=True)
    rfk.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    """show = session.query(rfk.Show).get(180)
    
    tags = 'penisrock pop post.rock schwarzmetall black.metal'
    
    
    show.updateTags(session,tags)
    """
    import datetime
    
    
    print rfk.Playlist.getCurrentItem(session).file
    session.commit()