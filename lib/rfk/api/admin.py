'''
Created on Jun 16, 2013

@author: teddydestodes
'''

from subprocess import call
import os
from datetime import datetime, timedelta

from flask import jsonify, request
from flask_login import current_user
from flaskext.babel import to_user_timezone

from rfk.liquidsoap.daemon import LiquidDaemonClient
from rfk.liquidsoap import LiquidInterface

from rfk.site.helper import permission_required
from rfk.site import app

from rfk.database.streaming import Relay
from rfk.database.stats import RelayStatistic

from rfk.helper import now

from rfk.api import api

@api.route("/site/admin/liquidsoap/endpoint/<string:action>")
@permission_required(permission='manage-liquidsoap')
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
@permission_required(permission='manage-liquidsoap')
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
@permission_required(permission='manage-liquidsoap')
def liquidsoap_start():
    returncode = call('rfk-liquidsoap')
    return jsonify({'status': returncode})

@api.route("/site/admin/liquidsoap/shutdown")
@permission_required(permission='manage-liquidsoap')
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
@permission_required(permission='manage-liquidsoap')
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
            ts = to_user_timezone(datetime.utcfromtimestamp(int(line[0])))
            lines.append((ts.isoformat(), line[1]))
        return jsonify({'log': lines, 'offset': offset})
    except Exception as e:
        return jsonify({'error': str(e)})

@api.route("/site/admin/feeds/sparkline/relay/<int:relay>/traffic")
@permission_required(permission='admin')
def relay_sparkline(relay):
    relay = Relay.query.get(relay)
    rs = RelayStatistic.get_relaystatistic(relay, RelayStatistic.TYPE.TRAFFIC)
    start = now()-timedelta(hours=6)
    dps = []
    for dp in rs.statistic.get(start=start, stop=now()):
        dps.append((int(dp.timestamp.strftime('%s')), dp.value))
    return jsonify({'datapoints': dps})