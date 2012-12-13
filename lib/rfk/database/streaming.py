from sqlalchemy import *
from sqlalchemy.orm import relationship, backref, exc

from rfk.database import Base

class Listener(Base):
    __tablename__ = 'listeners'
    listener = Column(Integer, primary_key=True, autoincrement=True)
    connect = Column(DateTime)
    disconnect = Column(DateTime)
    location = Column(String)
    stream_relay_id = Column("stream_relay",
                             Integer,
                             ForeignKey('stream_relays.stream_relay',
                                                        onupdate="CASCADE",
                                                        ondelete="RESTRICT"))
    stream_relay = relationship("StreamRelay")

class Stream(Base):
    __tablename__ = 'streams'
    stream = Column(Integer, primary_key=True, autoincrement=True)
    
    
class Relay(Base):
    __tablename__ = 'relays'
    relay = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String)
    port = Column(Integer)
    flag = Column(Integer)
    
class StreamRelay(Base):
    __tablename__ = 'stream_relays'
    stream_relay = Column(Integer, primary_key=True, autoincrement=True)