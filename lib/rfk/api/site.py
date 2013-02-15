'''
Created on Feb 15, 2013

@author: teddydestodes
'''

from rfk.api import api, check_auth, wrapper
from flask import jsonify, request, g

from rfk.database.streaming import ListenerStats, Stream
from rfk.database.show import Show
from sqlalchemy.sql.expression import between

import pytz
import parsedatetime.parsedatetime as pdt
from time import mktime
from datetime import datetime

def parse_datetimestring(datestring):
    cal = pdt.Calendar()
    return datetime.fromtimestamp(mktime(cal.parse(datestring)[0]))

@api.route("/site/listenergraphdata/<string:start>", methods=['GET'], defaults={'stop': 'now'})
@api.route("/site/listenergraphdata/<string:start>/<string:stop>", methods=['GET'])
def listenerdata(start,stop):
    from rfk.site import app
    app.logger.warn(start)
    app.logger.warn(stop)
    #detemine a starting point, wont be needed in productive code
    stop = parse_datetimestring(stop)
    start = parse_datetimestring(start)
    ls = ListenerStats.get(start)
    ret = {'data':{}, 'shows':[]}
    
    streams = Stream.query.all()
    for stream in streams:
        ret['data'][str(stream.mount)] = []
        #just set an initial stating point from before the starting point
        fls = ListenerStats.query.filter(ListenerStats.stream == stream,
                                         ListenerStats.timestamp <= start)\
                                 .order_by(ListenerStats.timestamp.desc()).limit(1).scalar()
        if fls is not None:
            c = fls.count
        else:
            c = 0
        ret['data'][str(stream.mount)].append((int(start.strftime("%s"))*1000,int(c)))
    
    #fill in the actual datapoints
    for stat in ls:
        ret['data'][str(stat.stream.mount)].append((int(stat.timestamp.strftime("%s"))*1000,int(stat.count)))
    
    for stream in streams:
        lls = ListenerStats.query.filter(ListenerStats.stream == stream,
                                         ListenerStats.timestamp <= stop)\
                                 .order_by(ListenerStats.timestamp.desc()).limit(1).scalar()
        if lls is not None:
            c = lls.count
        else:
            c = 0
        ret['data'][str(stream.mount)].append((int(stop.strftime("%s"))*1000,int(c)))
        
    #get the shows for the graph
    shows = Show.query.filter(between(Show.begin, start, stop)\
                            | between(Show.end, start, stop)).order_by(Show.begin.asc()).all()
    for show in shows:
        ret['shows'].append({'name': show.name,
                             'b':int(show.begin.strftime("%s")),
                             'e':int(show.end.strftime("%s")),})
    return jsonify(ret)