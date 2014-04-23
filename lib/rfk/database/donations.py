from sqlalchemy import *
from sqlalchemy.dialects.mysql import INTEGER as Integer
from rfk.types import ENUM

from rfk.database import Base, UTCDateTime
from rfk.helper import now


class Donation(Base):
    __tablename__ = 'donations'

    donation = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    value = Column(String(10), nullable=False)
    currency = Column(String(10), nullable=False)
    method = Column(Integer(unsigned=True), nullable=False)
    reference = Column(String(255))
    date = Column(UTCDateTime, default=now, nullable=False)
    country = Column(String(3))
    comment = Column(String(255))

    METHOD = ENUM(['BTC', 'MANUAL'])

