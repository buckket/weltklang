from flask import Flask, session, g, render_template, flash, redirect, url_for, request, jsonify, abort
from flask.ext.login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flaskext.babel import Babel, get_locale, get_timezone, refresh
import pytz
import datetime

from rfk.helper import now
from rfk.database import session
from rfk.database.base import User, Anonymous, News
from rfk.database.donations import Donation
from rfk.database.streaming import Stream
from rfk.site.forms.login import login_form, register_form
from rfk.site.forms.settings import SettingsForm
from rfk.exc.base import UserNameTakenException
from . import helper

app = Flask(__name__,instance_relative_config=True)
app.config['DEBUG'] = True
app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Berlin'
app.config['BABEL_DEFAULT_LOCALE'] = 'de'
app.config['BABEL_LOCALE_PATH'] = 'de'
app.secret_key = 'PENISPENISPENISPENISPENIS'

locales = {'de': {'name':'Bernd','img':'/static/img/cb/de.png', 'datetime_format': 'dd.MM.yyyy hh:mm'},
           'en': {'name':'English','img':'/static/img/cb/gb.png', 'datetime_format': 'MM/dd/yyyy hh:mm'}}

def get_datetime_format():
    try:
        return locales[str(get_locale())]['datetime_format']
    except KeyError:
        return locales['de']['datetime_format']


app.jinja_env.filters.update(bbcode=helper.bbcode,
                             timedelta=helper.timedelta
                             )


app.jinja_env.globals.update(nowPlaying= helper.nowPlaying)

babel = Babel(app)

@app.teardown_request
def shutdown_session(exception=None):
    session.remove()

@babel.localeselector
def babel_localeselector():
    if hasattr(g, 'current_locale'):
        return g.current_locale  
    elif request.cookies.get('locale') is not None:
        return request.cookies.get('locale')
    elif current_user is not None:
        return current_user.get_locale()
    return request.accept_languages.best_match(locales.keys())

@babel.timezoneselector
def babel_timezoneselector():
    if hasattr(g, 'current_timezone'):
        return g.current_timezone
    elif request.cookies.get('timezone') is not None:
        return request.cookies.get('timezone')
    elif current_user is not None:
        return current_user.get_timezone()
    return 'Europe/Berlin';
    

login_manager = LoginManager()
login_manager.setup_app(app)

login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
#login_manager.refresh_view = "reauth"

@login_manager.user_loader
def load_user(userid):
    return User.get_user(id=int(userid))

from . import user
app.register_blueprint(user.user, url_prefix='/user')
from . import show
app.register_blueprint(show.show)
from . import admin
app.register_blueprint(admin.admin, url_prefix='/admin')
from . import listen
app.register_blueprint(listen.listen, url_prefix='/listen')
from rfk.api import api
app.register_blueprint(api, url_prefix='/api')
from rfk.feeds import feeds
app.register_blueprint(feeds, url_prefix='/feeds')
from . import backend
app.register_blueprint(backend.backend, url_prefix='/backend')

def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f

@app.after_request
def call_after_request_callbacks(response):
    for callback in getattr(g, 'after_request_callbacks', ()):
        response = callback(response)
    return response


@app.before_request
def before_request():
    if request.method == 'GET': 
        if request.args.get('lang') is not None and request.args.get('lang') != '':
            current_user.locale = request.args.get('lang')
            g.current_locale = request.args.get('lang')
            @after_this_request
            def remember_locale(response):
                response.set_cookie('locale', current_user.locale, expires=datetime.datetime.utcnow()+datetime.timedelta(days=365))
                return response
        if request.args.get('tz') is not None and\
           request.args.get('tz') in pytz.common_timezones:
            current_user.timezone = request.args.get('tz')
            g.current_timezone = request.args.get('tz')
            @after_this_request
            def remember_timezone(response):
                response.set_cookie('timezone', current_user.timezone)
                return response
    refresh()
    request.current_locale = get_locale()
    request.current_timezone = str(get_timezone())

@app.before_request
def make_menu():
    request.menu = {}
    entries = [['index', 'Home']]
    
    request.menu['app.home'] = {'name': entries[0][1],
                                'url': url_for(entries[0][0]), 'active':(entries[0][0] == request.endpoint) }
    
    for bpname in app.blueprints.keys():
        try:
            request.menu[bpname] = app.blueprints[bpname].create_menu(request.endpoint)
        except AttributeError:
            pass


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


@app.route('/')
def index():
    news = News.query.all()
    streams = Stream.query.all()
    #print app.template_folder
    return render_template('index.html', news=news, streams=streams)


@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

@app.route('/login', methods=["GET", "POST"])
def login():
    form = login_form(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        user = User.get_user(username=username)
        if user and user.check_password(password=form.password.data):
            user.authenticated = True
            remember = form.remember.data
            if login_user(user, remember=remember):
                user.last_login = now()
                session.commit()
                flash("Logged in!")
                return redirect(request.args.get("next") or url_for("index"))
            else:
                form.username.errors.append('There was an error while logging you in.')
                flash("Sorry, but you could not log in.")
        else:
            form.username.errors.append('Invalid User or Password.')
            flash(u"Invalid username or password.")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    form = register_form(request.form)
    if request.method == "POST" and form.validate():
        try:
            user = User.add_user(form.username.data, form.password.data)
            if form.email.data:
                user.mail = form.email.data
            session.commit()
        except UserNameTakenException:
            form.username.errors.append('Username already taken!')
            
    return render_template("register.html", form=form)


@app.route('/settings', methods=['get', 'post'])
@login_required
def settings():
    
    form = SettingsForm(request.form,
                        username=current_user.username,
                        email=current_user.mail,
                        show_def_name=current_user.get_setting(code='show_def_name'),
                        show_def_desc=current_user.get_setting(code='show_def_desc'),
                        show_def_tags=current_user.get_setting(code='show_def_tags'),
                        show_def_logo=current_user.get_setting(code='show_def_logo'),
                        use_icy=current_user.get_setting(code='use_icy'))
    
    if request.method == "POST" and form.validate():
        if current_user.check_password(password=form.old_password.data):
            if form.new_password.data:
                current_user.password = User.make_password(form.new_password.data)
            current_user.mail = form.email.data
            current_user.set_setting(code='show_def_name', value=form.show_def_name.data)
            current_user.set_setting(code='show_def_desc', value=form.show_def_desc.data)
            current_user.set_setting(code='show_def_tags', value=form.show_def_tags.data)
            current_user.set_setting(code='show_def_logo', value=form.show_def_logo.data)
            current_user.set_setting(code='use_icy', value=form.use_icy.data)
            session.commit()
            flash('Settings successfully updated.')
            return redirect(url_for('settings'))
        else:
            form.old_password.errors.append('Wrong password.')

    return render_template('settings.html', form=form, username=current_user.username, TITLE='Settings')


@app.route('/donations')
def donations():
    donations = Donation.query.all()
    if donations:
        return render_template('donations.html', donations=donations)
    else:
        abort(500)


@app.route('/listeners')
def listeners():
    return render_template("listenergraph.html")    

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()