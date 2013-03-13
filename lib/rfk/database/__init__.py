from sqlalchemy import create_engine, types
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import pytz

Base = declarative_base()
session = None
engine = None

class UTCDateTime(types.TypeDecorator):

    impl = types.DateTime

    def process_bind_param(self, value, engine):
        if value is not None:
            if value.tzinfo is None:
                return pytz.utc.localize(value)
            else:
                return pytz.utc.normalize(value.astimezone(pytz.utc))

    def process_result_value(self, value, engine):
        if value is not None:
            return pytz.utc.localize(value)

import base
import show
import streaming
import track
import stats

def init_db(db_uri, debug=False):
    global session, engine
    engine = create_engine(db_uri, echo=debug)
    session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=True,
                                         bind=engine))
    Base.query = session.query_property()
    Base.metadata.create_all(bind=engine)
    Base.query = session.query_property()
    