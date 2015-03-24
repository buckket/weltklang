import datetime

from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask.ext.login import login_required, current_user
from flask.ext.babel import to_user_timezone, to_utc, gettext

from rfk import CONFIG
import rfk.database
from rfk.database.show import Show, Series
from rfk.helper import natural_join, make_user_link, now
from rfk.site import get_datetime_format
from rfk.site.forms.show import new_series_form


show = Blueprint('show', __name__)


@show.route('/shows/', defaults={'page': 1})
@show.route('/shows/upcoming', defaults={'page': 1})
@show.route('/shows/upcoming/<int:page>')
def upcoming(page):
    shows = Show.query.filter(Show.end > now()).order_by(Show.end.asc()).all()
    return render_template('shows/upcoming.html', TITLE=gettext('Shows'), shows=shows)


@show.route('/show/last')
def last():
    return 'blah'  # whatever :--D


@show.route('/series')
def list_series():
    series = Series.query.order_by(Series.name.asc()).all()
    return render_template('shows/series.html', TITLE=gettext('Series'), series=series)


@show.route('/series/new', methods=["GET", "POST"])
@login_required
def new_series():
    form = new_series_form(request.form)
    if request.method == "POST" and form.validate():
        series = Series(user=current_user,
                        public=form.public.data,
                        name=form.name.data,
                        description=form.description.data,
                        logo=form.image.data)
        rfk.database.session.add(series)
        rfk.database.session.commit()
        flash(gettext('Series added successfully'), 'info')
        return redirect(url_for('.list_series'))
    return render_template('shows/seriesform.html', form=form,
                           imgur={'client': CONFIG.get('site', 'imgur-client')})


@show.route('/schedule/week')
def calendar_week():
    now = to_user_timezone(datetime.datetime.utcnow()).date()
    return calendar_week_spec(int(now.strftime('%Y')), int(now.strftime('%W')) + 1)


@show.route('/schedule/week/<int:year>/<int:week>')
def calendar_week_spec(year, week):
    if week < 1:
        week = 1
    sunday = datetime.datetime.strptime("%s %s 0" % (year, week - 1), "%Y %W %w")
    monday = sunday - datetime.timedelta(days=6)
    begin = to_utc(monday + datetime.timedelta(hours=8))
    days = {}

    for wd in range(0, 7):
        days[wd] = _get_shows(begin, begin + datetime.timedelta(hours=24))
        begin = begin + datetime.timedelta(hours=24)

    #app.logger.warn(days)
    next_week = (sunday + datetime.timedelta(days=1))
    prev_week = (sunday + datetime.timedelta(days=-7))
    return render_template('shows/calendar/week.html',
                           TITLE=gettext('Schedule :: Week'),
                           shows=days,
                           year=year,
                           week=week,
                           monday=monday.date(),
                           sunday=sunday.date(),
                           next_week=url_for('.calendar_week_spec', year=next_week.strftime('%Y'),
                                             week=int(next_week.strftime('%W')) + 1),
                           prev_week=url_for('.calendar_week_spec', year=prev_week.strftime('%Y'),
                                             week=int(prev_week.strftime('%W')) + 1)
    )


@show.route('/show/new')
def new_show_form():
    if request.args.get('inline'):
        template = '/shows/showform-inline.html'
    else:
        template = '/shows/showform.html'
    return render_template(template,
                           imgur={'client': CONFIG.get('site', 'imgur-client')},
                           format=get_datetime_format())


@show.route('/show/<int:show>')
def show_view(show):
    s = Show.query.get(show)
    if s is None:
        return 'no show found'
        # TODO: proper error page
    if request.args.get('inline'):
        template = '/shows/show-inline.html'
    else:
        template = '/shows/show.html'

    link_users = []
    users = []
    for ushow in s.users:
        link_users.append(make_user_link(ushow.user))
        users.append(ushow.user)
    return render_template(template,
                           show={'name': s.name,
                                 'description': s.description,
                                 'series': s.series,
                                 'users': natural_join(link_users),
                                 'tags': s.tags,
                                 'begin': s.begin,
                                 'end': s.end,
                                 'logo': s.get_logo(),
                                 'user': users,
                                 'show': s.show,
                                 'duration': (s.end - s.begin).total_seconds(),
                                 'link': url_for('.show_view', show=s.show),
                                 'fulfilled': s.is_fulfilled()})


@show.route('/show/<int:show>/edit')
def show_edit(show):
    s = Show.query.get(show)
    if s is None:
        return 'no show found'
        # TODO: proper error page
    if request.args.get('inline'):
        template = '/shows/showform-inline.html'
    else:
        template = '/shows/showform.html'

    tags = []
    for tag in s.tags:
        tags.append(tag.tag.name)

    return render_template(template,
                           show={'name': s.name,
                                 'description': s.description,
                                 'series': s.series,
                                 'users': s.users,
                                 'tags': ",".join(tags),
                                 'begin': to_user_timezone(s.begin).strftime('%s'),
                                 'logo': s.logo,
                                 'show': s.show,
                                 'duration': (s.end - s.begin).total_seconds() / 60},
                           imgur={'client': CONFIG.get('site', 'imgur-client')},
                           format=get_datetime_format())


def _get_shows(begin, end):
    shows = Show.query.filter(Show.end > begin, Show.begin < end).all()
    planned = []
    unplanned = []
    for show in shows:
        b = show.begin
        e = show.end
        if b < begin:
            b = begin
        if e > end:
            e = end
        t = {'show': show.show,
             'offset': (b - begin).total_seconds(),
             'duration': (e - b).total_seconds(),
             'name': show.name,
             'description': show.description,
             'fulfilled': show.is_fulfilled(),
             'tags': []}
        for tag in show.tags:
            if tag.tag.icon and len(tag.tag.icon) > 0:
                t['tags'].append({'icon': tag.tag.icon, 'alt': tag.tag.description})
        if show.flags & Show.FLAGS.RECORD:
            t['tags'].append({'icon': 'icon-save', 'alt': ''})
        if show.flags & Show.FLAGS.PLANNED:
            planned.append(t)
        elif show.flags & Show.FLAGS.UNPLANNED:
            unplanned.append(t)
    return (planned, unplanned)


def create_menu(endpoint):
    menu = {'name': gettext('Programme'), 'submenu': [], 'active': False}
    entries = [['show.upcoming', gettext('Upcoming Shows')],
               ['show.list_series', gettext('Series')],
               ['show.calendar_week', gettext('Schedule')]]
    for entry in entries:
        active = endpoint == entry[0]
        menu['submenu'].append({'name': entry[1],
                                'url': url_for(entry[0]),
                                'active': (active)})
        if active:
            menu['active'] = True
    return menu


show.create_menu = create_menu
