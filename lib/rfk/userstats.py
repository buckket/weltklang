#!/usr/bin/env python

import sys

from sqlalchemy.orm import exc

import rfk
import rfk.database
from rfk.helper import now
from rfk.database import init_db
from rfk.database.base import User
from rfk.database.show import Show, UserShow, Role
from rfk.database.streaming import Listener
from rfk.database.stats import Statistic
from rfk.database.stats import UserStatistic


def generate_listener_peak(user):
    role_host = Role.get_role('host')
    user_listener_max = 0

    shows = Show.query.join(UserShow).filter(UserShow.user == user,
                                             UserShow.role == role_host,
                                             UserShow.status == UserShow.STATUS.STREAMED,
                                             Show.end <= now()).yield_per(50)

    for show in shows:
        try:
            stats_total = Statistic.query.filter(Statistic.identifier == 'lst-total').one()
            stats = stats_total.get(start=show.begin, stop=show.end)
        except exc.NoResultFound:
            stats = None

        if stats and stats.count() > 0:
            for stat in stats:
                if stat.value > user_listener_max:
                    user_listener_max = stat.value

    if user_listener_max > 0:
        us = UserStatistic.get_userstatistic(user, 'listenerpeak')
        us.statistic.set(now(), user_listener_max)
        rfk.database.session.flush()


def generate_listenerhours(user):
    role_host = Role.get_role('host')
    total_listener_hours = 0

    for usershow in UserShow.query.filter(UserShow.user == user,
                                          UserShow.role == role_host,
                                          UserShow.status == UserShow.STATUS.STREAMED).yield_per(50):

        for listener in Listener.query.filter(Listener.connect <= usershow.show.end,
                                              usershow.show.begin <= Listener.disconnect).all():
            s = listener.connect
            if s < usershow.show.begin:
                s = usershow.show.begin
            e = listener.disconnect
            if e > usershow.show.end:
                e = usershow.show.end
            listener_time = e - s
            if listener_time.total_seconds() >= 0:
                total_listener_hours += listener_time.total_seconds()/3600
            else:
                print 'something went wrong: negative listenertime isn\'t possible'

    if total_listener_hours > 0 or True:
        us = UserStatistic.get_userstatistic(user, 'listenerhours')
        us.statistic.set(now(), total_listener_hours)
        rfk.database.session.flush()


def generate_missed_show_ratio(user):
    role_host = Role.get_role('host')
    missed_shows = 0
    total_shows = 0

    for usershow in UserShow.query.join(Show).filter(UserShow.user == user,
                                                     UserShow.role == role_host,
                                                     Show.flags == Show.FLAGS.PLANNED,
                                                     Show.end <= now()).yield_per(50):

        total_shows += 1
        if usershow.status != UserShow.STATUS.STREAMED:
            missed_shows += 1

    if total_shows > 0:
        missed_show_ratio = (float(missed_shows)/float(total_shows))*100

        us = UserStatistic.get_userstatistic(user, 'missedshowratio')
        us.statistic.set(now(), missed_show_ratio)
        rfk.database.session.flush()


stats = [generate_listener_peak,
         generate_listenerhours,
         generate_missed_show_ratio]


def main():
    try:
        rfk.init()
        if rfk.CONFIG.has_option('database', 'url'):
            init_db(rfk.CONFIG.get('database', 'url'))
        else:
            init_db("%s://%s:%s@%s/%s" % (rfk.CONFIG.get('database', 'engine'),
                                          rfk.CONFIG.get('database', 'username'),
                                          rfk.CONFIG.get('database', 'password'),
                                          rfk.CONFIG.get('database', 'host'),
                                          rfk.CONFIG.get('database', 'database')))
        for user in User.query.yield_per(50):
            for stat in stats:
                stat(user)
        rfk.database.session.commit()
    except Exception as e:
        rfk.database.session.rollback()
        raise
    finally:
        rfk.database.session.remove()


if __name__ == '__main__':
    sys.exit(main())
