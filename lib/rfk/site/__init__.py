from flask import Flask, session, g, render_template, flash, redirect, url_for, request, jsonify
from flask.ext.login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flaskext.babel import Babel
import datetime

from rfk.database import session
from rfk.database.base import User, Anonymous, News
from . import helper

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Berlin'
app.config['BABEL_DEFAULT_LOCALE'] = 'de'
app.config['BABEL_LOCALE_PATH'] = 'de'
app.secret_key = 'PENISPENISPENISPENISPENIS'

app.jinja_env.globals['nowPlaying'] = helper.nowPlaying
app.jinja_env.filters['bbcode'] = helper.bbcode
app.jinja_env.filters['timedelta'] = helper.timedelta

babel = Babel(app)

@app.teardown_request
def shutdown_session(exception=None):
    session.remove()

@babel.localeselector
def get_locale():
    if current_user is not None:
        return current_user.locale
    return request.accept_languages.best_match(['de', 'en'])

@babel.timezoneselector
def get_timezone():
    if request.cookies.get('timezone') is not None:
        request.cookies.get('timezone')
    if current_user is not None:
        return current_user.timezone

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
from . import register
app.register_blueprint(register.register)
from rfk.api import api
app.register_blueprint(api, url_prefix='/api')
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
            @after_this_request
            def remember_locale(response):
                response.set_cookie('locale', current_user.locale, expires=datetime.datetime.utcnow()+datetime.timedelta(days=365))
                return response
        if request.args.get('tz') is not None and request.args.get('tz') != '':
            current_user.timezone = request.args.get('tz')
            @after_this_request
            def remember_timezone(response):
                response.set_cookie('timezone', current_user.timezone)
                return response

@app.before_request
def make_menu():
    request.menu = {}
    for bpname in app.blueprints.keys():
        try:
            request.menu[bpname] = app.blueprints[bpname].create_menu()
        except AttributeError:
            pass

@app.route('/timezones')
def timezones():
    import pytz
    regions = {}
    for tz in pytz.common_timezones:
        zone = tz.split('/',1)
        if zone[0] not in regions.keys():
            regions[zone[0]] = []
        try:
            regions[zone[0]].append(zone[1])
        except IndexError:
            pass
    response = jsonify(regions);
    return response

locales = {'de': {'name':'Bernd','img':'/static/img/cb/de.png'},
           'en': {'name':'English','img':'/static/img/cb/gb.png'}}
@app.route('/locales')
def get_locales():
    response = jsonify(locales)
    return response

@app.route('/locale/<locale>')
def get_localeinfo(locale):
    response = jsonify(locales[locale])
    return response

@app.route('/')
def index():
    news = News.query.all()
    #print app.template_folder
    return render_template('index.html', news=news)

@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST" and "username" in request.form:
        username = request.form["username"]
        user = User.get_user(username=username)
        if user and user.check_password(password=request.form['password']):
            user.authenticated = True
            remember = request.form.get("remember", "no") == "yes"
            if login_user(user, remember=remember):
                flash("Logged in!")
                return redirect(request.args.get("next") or url_for("index"))
            else:
                flash("Sorry, but you could not log in.")
        else:
            flash(u"Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))



def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()