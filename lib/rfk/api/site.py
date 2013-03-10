from flask import jsonify, request, g
from sqlalchemy.sql.expression import between
import pytz
import parsedatetime.parsedatetime as pdt
from time import mktime
from datetime import datetime
from subprocess import call
import os

from rfk.api import api, check_auth, wrapper
#from rfk.database.streaming import ListenerStats, Stream
from rfk.database.show import Show
from rfk.liquidsoap.daemon import LiquidDaemonClient
from rfk.liquidsoap import LiquidInterface
from rfk.site import app

@api.route("/site/admin/liquidsoap/endpoint/<string:action>")
def endpoint_action(action):
    if request.args.get('endpoint') is None:
        return jsonify({'error':'no endpoint supplied!'})
    try:
        ret = {}
        li = LiquidInterface()
        li.connect()
        ret['status'] = li.endpoint_action(request.args.get('endpoint').encode('ascii','ignore'),
                                           action.encode('ascii','ignore'))
        li.close()
        return jsonify(ret)
    except Exception as e:
        return jsonify({'error': str(e)})

@api.route("/site/admin/liquidsoap/status")
def liquidsoap_status():
    try:
        ret = {}
        li = LiquidInterface()
        li.connect()
        ret['version'] = li.get_version()
        ret['uptime'] = li.get_uptime()
        ret['sources'] = []
        for source in li.get_sources():
            ret['sources'].append({'handler': source.handler,
                                   'type': source.type,
                                   'status': (source.status() != 'no source client connected'),
                                   'status_msg':source.status()})
            
        ret['sinks'] = []
        for sink in li.get_sinks():
            ret['sinks'].append({'handler': sink.handler,
                                   'type': sink.type,
                                   'status': (sink.status() == 'on')})
        li.close()
        return jsonify(ret)
    except Exception as e:
        return jsonify({'error': str(e)})

@api.route("/site/admin/liquidsoap/start")
def liquidsoap_start():
    returncode = call([os.path.join(app.config['BASEDIR'], 'bin','run-liquid.py')])
    return jsonify({'status': returncode})

@api.route("/site/admin/liquidsoap/shutdown")
def liquidsoap_shutdown():
    try:
        client = LiquidDaemonClient()
        client.connect()
        client.shutdown_daemon()
        client.close()
        return jsonify({'status': 'done'})
    except Exception as e:
        return jsonify({'error': str(e)})

@api.route("/site/admin/liquidsoap/log")
def liquidsoap_log():
    try:
        client = LiquidDaemonClient()
        client.connect()
        offset = request.args.get('offset')
        if offset is not None:
            offset = int(offset)
        
        offset, log = client.get_log(offset)
        client.close()
        lines = []
        for line in log:
            ts = pytz.utc.localize(datetime.utcfromtimestamp(int(line[0])))
            lines.append((ts.isoformat(), line[1]))
        return jsonify({'log': lines, 'offset': offset})
    except Exception as e:
        return jsonify({'error': str(e)})

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
        fls = ListenerStats.query.filter(ListenerStats.timestamp <= start,
                                         ListenerStats.stream == stream)\
                                 .order_by(ListenerStats.timestamp.desc()).limit(1).scalar()
        if fls is not None:
            c = fls.count
        else:
            c = 0
        ret['data'][str(stream.mount)].append((int(start.strftime("%s"))*1000,int(c)))
    
    #fill in the actual datapoints
    ls = ListenerStats.get(start, stop=stop)
    for stat in ls:
        ret['data'][str(stat.stream.mount)].append((int(stat.timestamp.strftime("%s"))*1000,int(stat.count)))
    
    for stream in streams:
        lls = ListenerStats.query.filter(ListenerStats.timestamp <= stop,
                                         ListenerStats.stream == stream)\
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
