from sqlalchemy import *
from sqlalchemy.orm import relationship, backref, exc
from sqlalchemy.dialects.mysql import INTEGER as Integer

import rfk.database
from rfk.database import Base, UTCDateTime
from rfk.helper import now

import pytz


class Track(Base):
    """Database representation of a Track played in a show"""
    __tablename__ = 'tracks'
    track = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    begin = Column(UTCDateTime())
    end = Column(UTCDateTime())
    title_id = Column("title", Integer(unsigned=True),
                      ForeignKey('titles.title',
                                 onupdate="CASCADE",
                                 ondelete="RESTRICT"))
    title = relationship("Title", backref=backref('tracks'))
    show_id = Column("show", Integer(unsigned=True),
                     ForeignKey('shows.show',
                                onupdate="CASCADE",
                                ondelete="RESTRICT"))
    show = relationship("Show", backref=backref('tracks'))

    @staticmethod
    def current_track():
        """returns the current track (not yet ended)"""
        try:
            return Track.query.filter(Track.end == None).one()
        except exc.NoResultFound:
            return None

    def end_track(self, end=None):
        """ends the track and updates length in artist/title DB"""
        if end is None:
            self.end = now()
        else:
            self.end = end
        length = self.end - self.begin
        self.title.update_length(length.total_seconds())

    @staticmethod
    def new_track(show, artist, title, begin=None):
        """adds a new Track to database and ends the current track (if any)"""
        if begin is None:
            current_track = Track.current_track()
            if current_track:
                current_track.end_track()
        title = Title.add_title(artist, title)
        if begin is None:
            begin = now()
        track = Track(title=title, begin=begin, show=show)
        rfk.database.session.add(track)
        rfk.database.session.flush()
        return track


"""Track Indices"""
Index('curr_track_idx', Track.end)


class Title(Base):
    """Artist/Title combination"""

    __tablename__ = 'titles'
    title = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    artist_id = Column("artist", Integer(unsigned=True),
                       ForeignKey('artists.artist',
                                  onupdate="CASCADE",
                                  ondelete="RESTRICT"))
    artist = relationship("Artist", backref=backref('titles'))
    name = Column(String(255))
    length = Column(Integer(unsigned=True), default=0)
    length_samples = Column(Integer(unsigned=True), default=0)

    def update_length(self, length):
        """updates the length of the track"""
        self.length = (length + self.length) / (self.length_samples + 1)
        self.length_samples += 1

    @staticmethod
    def add_title(artist, title, length=None):
        """adds and returns a new track to the database, or returns a track if it's already exsisting"""
        try:
            t = Title.query.join(MetaTitle). \
                join(Artist). \
                join(MetaArtist). \
                filter(MetaTitle.name == title,
                       MetaArtist.name == artist).one()
        except exc.NoResultFound:
            a = Artist.get_artist(artist)
            t = Title(artist=a, name=title)
            rfk.database.session.add(t)
            rfk.database.session.flush()

        try:
            m = MetaTitle.query.filter(MetaTitle.title == t, MetaTitle.name == title).one()
        except exc.NoResultFound:
            m = MetaTitle(name=title, title=t)
            rfk.database.session.add(m)
            rfk.database.session.flush()

        if length is not None:
            m.update_length(length)
        return t


class MetaTitle(Base):
    """Metaclass for Titles
       this should not be used outside of Track()
    """
    __tablename__ = 'metatitles'
    metatitle = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    title_id = Column("title", Integer(unsigned=True),
                      ForeignKey('titles.title',
                                 onupdate="CASCADE",
                                 ondelete="RESTRICT"))
    title = relationship("Title", backref=backref('metatitles'))
    name = Column(String(255))


class Artist(Base):
    """Artist representation in Database"""
    __tablename__ = 'artists'
    artist = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)

    @staticmethod
    def get_artist(name):
        """returns an Artist object for name"""
        metaartist = MetaArtist.get_metaartist(name)
        if metaartist.artist is None:
            artist = Artist(name=name)
            metaartist.artist = artist
            rfk.database.session.add(artist)
            rfk.database.session.flush()
            return artist
        else:
            return metaartist.artist


class MetaArtist(Base):
    """Metaclass for Artists
       this should not be used outside of Artist()
    """
    __tablename__ = 'metaartists'
    metaartist = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    artist_id = Column("artist", Integer(unsigned=True),
                       ForeignKey('artists.artist',
                                  onupdate="CASCADE",
                                  ondelete="RESTRICT"))
    artist = relationship("Artist", backref=backref('metaartists'))
    name = Column(String(255), unique=True)

    @staticmethod
    def get_metaartist(name):
        """returns an MetaArtist object for name"""
        try:
            return MetaArtist.query.filter(MetaArtist.name == name).one()
        except exc.NoResultFound:
            ma = MetaArtist(name=name)
            rfk.database.session.add(ma)
            rfk.database.session.flush()
            return ma
