'''
Created on 30.04.2012

@author: teddydestodes
'''
import rfk
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref,sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Streamer(Base):
    __tablename__ = 'streamer'
    streamer = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    password = Column(String)
    streampassword = Column(String)
    ban      = Column(DateTime) 

class Show(Base):
    __tablename__ = 'shows'
    show = Column(Integer, primary_key=True, autoincrement=True)
    streamer_id = Column('streamer', Integer(unsigned=True), ForeignKey('streamer.streamer', onupdate="CASCADE", ondelete="RESTRICT"))
    streamer = relationship('Streamer', backref='shows')
    name = Column(String)
    description = Column(String)
    begin = Column(DateTime)
    end = Column(DateTime)
    

old_engine = create_engine('mysql://radio:penis@localhost/radio?charset=utf8')
engine = create_engine('sqlite:///data.db')

rfk.Base.metadata.create_all(engine)

if __name__ == '__main__':
    OldSession = sessionmaker(bind=old_engine)
    oldsession = OldSession()
    Session = sessionmaker(bind=engine)
    session = Session()
    streamer = oldsession.query(Streamer).all()
    
    for olduser in streamer:
        print olduser.username
        user = session.query(rfk.User).filter(rfk.User.name == olduser.username).first()
        if user == None:
            user = rfk.User(olduser.username, olduser.password, rfk.User.makePassword(olduser.streampassword))
            session.add(user)
    session.commit()
    
    shows = oldsession.query(Show).all()
    print len(shows)
    for oldshow in shows:
        print oldshow.show
        show = rfk.Show(name=oldshow.name, description=oldshow.description, begin=oldshow.begin, end=oldshow.end)
        user = session.query(rfk.User).filter(rfk.User.name == oldshow.streamer.username).first()
        show.users.append(user)
        session.add(show)
    session.commit()