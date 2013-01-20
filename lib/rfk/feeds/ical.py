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
    cal = Calendar()
    cal.add('prodid', '-//Radio freies Krautchan//EN')
    cal.add('version', '2.0')
    cal.add('method', 'PUBLISH' )
      
    # add some useful iCal extensions
    cal.add('x-wr-calname', 'RfK')
    cal.add('x-wr-caldesc', 'Radio freies Krautchan')
    cal.add('x-wr-timezone', 'UTC')
    
    clauses = []
    clauses.append(Show.end > datetime.utcnow())
    result = Show.query.join(UserShow).join(User).filter(*clauses).order_by(Show.begin.asc()).all()
    
    if result:
        for show in result:
            # add the shows
            event = Event()
            event.add('summary', show.name)
            event.add('description', show.description)
            event.add('dtstart', show.begin)
            event.add('dtend', show.end)
            cal.add_component(event)
            
    return cal.to_ical()
    #return Response(cal.to_ical(), mimetype='text/calendar')
