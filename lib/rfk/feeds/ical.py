from flask import Response
from icalendar import Calendar, Event
from rfk.feeds import feeds, get_shows


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
    
    # adding planned shows
    result = get_shows()
    
    if result:
        for show in result:
            event = Event()
            event.add('uid', str(show.show))
            event.add('summary', show.name)
            event.add('description', show.description)
            event.add('dtstart', show.begin)
            event.add('dtend', show.end)
            cal.add_component(event)
            
    return Response(cal.to_ical(), mimetype='text/calendar')
