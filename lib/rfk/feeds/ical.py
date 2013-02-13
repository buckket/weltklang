import pytz

from flask import Response
from datetime import datetime
from icalendar import Calendar, Event

from rfk.feeds import feeds
import rfk.database
from rfk.database.base import User
from rfk.database.show import Show, UserShow

@feeds.route('/ical')
def ical():
        
    # init calendar
    utc = pytz.utc
    cal = Calendar()
    cal.add('prodid', '-//Radio freies Krautchan//EN')
    cal.add('version', '2.0')
    cal.add('method', 'PUBLISH' )
      
    # add some useful iCal extensions
    cal.add('x-wr-calname', 'RfK')
    cal.add('x-wr-caldesc', 'Radio freies Krautchan')
    cal.add('x-wr-timezone', 'UTC')
    
    # adding planned shows
    clauses = []
    clauses.append(Show.end > datetime.utcnow())
    result = Show.query.join(UserShow).join(User).filter(*clauses).order_by(Show.begin.asc()).all()
    
    if result:
        for show in result:
            event = Event()
            event.add('uid', show.show)
            event.add('summary', show.name)
            event.add('description', show.description)
            event.add('dtstart', utc.localize(show.begin))
            event.add('dtend', utc.localize(show.end))
            cal.add_component(event)
            
    return Response(cal.to_ical(), mimetype='text/calendar')
