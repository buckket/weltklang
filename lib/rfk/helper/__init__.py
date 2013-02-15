import pytz
import datetime

def now():
    return pytz.utc.localize(datetime.datetime.utcnow())
