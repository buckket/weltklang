from sqlalchemy import *
from sqlalchemy.dialects.mysql import INTEGER as Integer

from rfk.database import Base, UTCDateTime
from rfk.helper import now


class Donation(Base):
    __tablename__ = 'donations'
    donation = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    in_value = Column(String(10))
    out_value = Column(String(10))
    in_currency = Column(String(10))
    out_currency = Column(String(10))
    date = Column(UTCDateTime, default=now())
    method = Column(String(20))
    country = Column(String(3))
