from sqlalchemy.orm.exc import NoResultFound

import rfk
import rfk.database
from rfk.database.streaming import Listener
from rfk.database.stats import Statistic


def update_stats_at(stats, datetime):
    c = Listener.query.filter(datetime >= Listener.connect,
                              datetime < Listener.disconnect).count()
    stats.set(datetime, c)

if __name__ == '__main__':
    rfk.init(enable_geoip=False)
    if rfk.CONFIG.has_option('database', 'url'):
        rfk.database.init_db(rfk.CONFIG.get('database', 'url'))
    else:
        rfk.database.init_db("%s://%s:%s@%s/%s" % (rfk.CONFIG.get('database', 'engine'),
                                                   rfk.CONFIG.get('database', 'username'),
                                                   rfk.CONFIG.get('database', 'password'),
                                                   rfk.CONFIG.get('database', 'host'),
                                                   rfk.CONFIG.get('database', 'database')))

    try:
        stat = Statistic.query.filter(Statistic.identifier == 'lst-total').one()
    except NoResultFound:
        stat = Statistic(name='Overall Listener', identifier='lst-total')
        rfk.database.session.add(stat)
        rfk.database.session.flush()
    for listener in Listener.query.order_by(Listener.listener.asc()).yield_per(50):
        print 'c',
        update_stats_at(stat, listener.connect)
        if listener.disconnect:
            print 'd',
            update_stats_at(stat, listener.disconnect)
