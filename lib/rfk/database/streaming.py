from sqlalchemy import *
from sqlalchemy.orm import relationship, backref, exc
from sqlalchemy.dialects.mysql import INTEGER as Integer
from datetime import datetime
import netaddr
import pygeoip

from rfk.database import Base, UTCDateTime
from rfk.types import ENUM, SET
from rfk import CONFIG
from rfk.helper import now, get_location
import rfk.database
import rfk.icecast


class Listener(Base):
    """database representation of a Listener"""
    __tablename__ = 'listeners'
    listener = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    connect = Column(UTCDateTime)
    disconnect = Column(UTCDateTime)
    country = Column(String(3))
    city = Column(String(50))
    address = Column(Integer(unsigned=True))
    client = Column(Integer(unsigned=True))
    useragent = Column(String(255))
    stream_relay_id = Column("stream_relay",
                             Integer(unsigned=True),
                             ForeignKey('stream_relays.stream_relay',
                                        onupdate="CASCADE",
                                        ondelete="RESTRICT"))
    stream_relay = relationship("StreamRelay")
    show_id = Column("show",Integer(unsigned=True),
                             ForeignKey('shows.show',
                                        onupdate="CASCADE",
                                        ondelete="RESTRICT"))
    show = relationship("Show")
    @staticmethod
    def get_listener(stream_relay, client, disconnect=None):
        """returns a listener"""
        listener = Listener.query.filter(Listener.disconnect == disconnect,
                                         Listener.stream_relay == stream_relay,
                                         Listener.client == client).one()
        return listener
        
    @staticmethod
    def create(address, client, useragent, stream_relay):
        """adds a new listener to the database"""
        listener = Listener()
        if rfk.CONFIG.getboolean('icecast', 'log_ip'):
            listener.address = int(netaddr.IPAddress(address))
        listener.client = client
        loc = get_location(address)
        if 'city' in loc:
            listener.city = loc['city'].decode('latin-1') #FICK DICH MAXMIND
        if 'country_code' in loc:
            listener.country = loc['country_code']
        listener.useragent = useragent
        listener.connect = now()
        listener.stream_relay = stream_relay
        rfk.database.session.add(listener)
        return listener
    
    def set_disconnected(self):
        """updates the listener to disconnected state"""
        self.disconnect = now()
        
class Stream(Base):
    """database representation of an outputStream"""
    __tablename__ = 'streams'
    stream = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    mount = Column(String(25))
    code = Column(String(25))
    name = Column(String(25))
    type = Column(Integer(unsigned=True))
    quality = Column(Integer)
    statistic_id = Column("statistic", Integer(unsigned=True), ForeignKey('statistics.statistic',
                                                                          onupdate="CASCADE",
                                                                          ondelete="RESTRICT"))
    statistic = relationship("Statistic")
    TYPES = ENUM(['UNKNOWN', 'MP3', 'AACP', 'OGG', 'OPUS'])
    
    @staticmethod
    def get_stream(id=None, mount=None):
        """returns a Stream by id or mountpoint"""
        assert id or mount
        if id:
            return Stream.query.get(id)
        else:
            return Stream.query.filter(Stream.mount == mount).one()
        
    def add_relay(self, relay):
        """adds a Relay to this Stream"""
        try:
            StreamRelay.query.filter(StreamRelay.stream == self,
                                     StreamRelay.relay == relay).one()
            return False
        except exc.NoResultFound:
            self.relays.append(StreamRelay(relay=relay))
            return True
    
class Relay(Base):
    """database representation of a RelayServer"""
    __tablename__ = 'relays'
    relay = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    address = Column(String(15))
    port = Column(Integer(unsigned=True))
    flag = Column(Integer(unsigned=True))
    bandwith = Column(Integer(unsigned=True))
    usage = Column(Integer(unsigned=True))
    admin_username = Column(String(50))
    admin_password = Column(String(50))
    auth_username = Column(String(50))
    auth_password = Column(String(50))
    relay_username = Column(String(50))
    relay_password = Column(String(50)) 
    type = Column(Integer(unsigned=True))
    status = Column(Integer(unsigned=True))
    statistic_id = Column("statistic", Integer(unsigned=True), ForeignKey('statistics.statistic',
                                                                          onupdate="CASCADE",
                                                                          ondelete="RESTRICT"))
    statistic = relationship("Statistic")
    STATUS = ENUM(['UNKNOWN', 'DISABLED', 'OFFLINE', 'ONLINE'])
    TYPE = ENUM(['MASTER', 'RELAY'])
    
    @staticmethod
    def get_master():
        """returns the master server"""
        return Relay.query.filter(Relay.type == Relay.TYPE.MASTER).one()
    
    @staticmethod
    def get_relay(id=None, address=None, port=None):
        """returns a Relay either by id or by address and port"""
        assert id or (address and port)
        if id:
            return Relay.query.get(id)
        else:
            return Relay.query.filter(Relay.address == address,
                                      Relay.port == port).one()
        
    def get_icecast_config(self, all_streams=False):
        """returns the configuration XML for this Relay"""
        conf = rfk.icecast.IcecastConfig()
        conf.address = self.address
        conf.port = self.port
        conf.admin = self.admin_username
        conf.password = self.admin_password
        conf.hostname = self.address
        api_url = "http://%s%s" % (CONFIG.get('site', 'url'),'/backend/icecast/')
        if all_streams:
            for stream in Stream.query.all():
                mount = rfk.icecast.Mount()
                mount.api_url = api_url 
                mount.mount = stream.mount
                mount.username = self.auth_username
                mount.password = self.auth_password
                conf.mounts.append(mount)
        else:
            for stream in self.streams:
                mount = rfk.icecast.Mount()
                mount.api_url = api_url
                mount.mount = stream.stream.mount
                mount.username = self.auth_username
                mount.password = self.auth_password
                conf.mounts.append(mount)
        if self.type == Relay.TYPE.RELAY:
            master = Relay.get_master()
            conf.master = master.address
            conf.master_user = master.relay_username
            conf.master_password = master.relay_password
            conf.master_port = master.port
        elif self.type == Relay.TYPE.MASTER:
            conf.relay_user = self.relay_username
            conf.relay_password = self.relay_password
        return conf.get_xml()
        
    def add_stream(self, stream):
        """adds a Stream to this Relay"""
        try:
            return StreamRelay.query.filter(StreamRelay.relay == self,
                                            StreamRelay.stream == stream).one()
        except exc.NoResultFound:
            return self.streams.append(StreamRelay(stream=stream))
            
    
    def get_stream_relay(self, stream):
        """returns the StreamRelay combination for the given Stream and this Relay"""
        return StreamRelay.query.filter(StreamRelay.relay == self,
                                        StreamRelay.stream == stream).one()
    
class StreamRelay(Base):
    __tablename__ = 'stream_relays'
    stream_relay = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    stream_id = Column("stream", Integer(unsigned=True), ForeignKey('streams.stream',
                                                 onupdate="CASCADE",
                                                 ondelete="RESTRICT"))
    stream = relationship("Stream", backref=backref('relays'))
    relay_id = Column("relay", Integer(unsigned=True),
                           ForeignKey('relays.relay',
                                      onupdate="CASCADE",
                                      ondelete="RESTRICT"))
    relay = relationship("Relay", backref=backref('streams'))
    status = Column(Integer(unsigned=True))
    statistic_id = Column("statistic", Integer(unsigned=True), ForeignKey('statistics.statistic',
                                                                          onupdate="CASCADE",
                                                                          ondelete="RESTRICT"))
    statistic = relationship("Statistic")
    STATUS = ENUM(['UNKNOWN', 'DISABLED', 'OFFLINE', 'ONLINE'])
    
    def __init__(self, relay=None, stream=None):
        assert relay or stream
        self.relay = relay
        self.stream = stream
        
    def set_offline(self):
        """sets this combination of stream and relay to offline"""
        self.status = StreamRelay.STATUS.OFFLINE
        connected_listeners = Listener.query.filter(Listener.stream_relay == self,
                                                    Listener.disconnect == None).all()
        for listener in connected_listeners:
            listener.disconnect = now()