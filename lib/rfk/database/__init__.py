from sqlalchemy import create_engine, types, text
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
                return value
            else:
                return pytz.utc.normalize(value.astimezone(pytz.utc)).replace(tzinfo=None)

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
    Base.metadata.create_all(bind=engine)
    Base.query = session.query_property()

def drop_all_tables_and_sequences():
    ''' 
    Drops all tables and sequences (but not VIEWS) from a postgres database
    '''

    sequence_sql='''SELECT sequence_name FROM information_schema.sequences
                    WHERE sequence_schema='public'
                 '''
    
    table_sql='''SELECT table_name FROM information_schema.tables
                 WHERE table_schema='public' AND table_type != 'VIEW' AND table_name NOT LIKE 'pg_ts_%%'
              '''

    for table in [name for (name, ) in engine.execute(text(table_sql))]:
        engine.execute(text('DROP TABLE %s CASCADE' % table))
     
    for seq in [name for (name, ) in engine.execute(text(sequence_sql))]:
        engine.execute(text('DROP SEQUENCE %s CASCADE' % seq))
    