import pytz
import datetime
import rfk

def now():
    return pytz.utc.localize(datetime.datetime.utcnow())

def get_location(address):
    return rfk.geoip.record_by_addr(address)