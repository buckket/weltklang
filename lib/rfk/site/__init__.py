from flask import Flask, session, g, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flaskext.babel import Babel

import rfk
from . import helper
from rfk.model import User, News

app = Flask(__name__, template_folder='/home/teddydestodes/src/PyRfK/var/template/',
                      static_folder='/home/teddydestodes/src/PyRfK/web_static/',
                      static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = "%s://%s:%s@%s/%s?charset=utf8" % (rfk.CONFIG.get('database', 'engine'),
                                                              rfk.CONFIG.get('database', 'username'),
                                                              rfk.CONFIG.get('database', 'password'),
                                                              rfk.CONFIG.get('database', 'host'),
                                                              rfk.CONFIG.get('database', 'database'))
app.config['DEBUG'] = True
app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Berlin'
app.config['BABEL_DEFAULT_LOCALE'] = 'de'
#app.config['BABEL_LOCALE_PATH'] = 'de'
app.secret_key = 'PENISPENISPENISPENISPENIS'

app.jinja_env.globals['nowPlaying'] = helper.nowPlaying
app.jinja_env.filters['bbcode'] = helper.bbcode
app.jinja_env.filters['timedelta'] = helper.timedelta

db = SQLAlchemy(app)
rfk.init_db(db.engine, db.Model.metadata)

babel = Babel(app)

@babel.localeselector
def get_locale():
    if current_user is not None:
        return current_user.locale
    return request.accept_languages.best_match(['de', 'en'])

@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone

login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
#login_manager.refresh_view = "reauth"

@login_manager.user_loader
def load_user(userid):
    return db.session.query(User).get(int(userid))

from . import user
app.register_blueprint(user.user, url_prefix='/user')
from . import show
app.register_blueprint(show.show, url_prefix='/show')
from . import admin
app.register_blueprint(admin.admin, url_prefix='/admin')
from . import listen
app.register_blueprint(listen.listen, url_prefix='/listen')
from . import register
app.register_blueprint(register.register)
from rfk.api import api
app.register_blueprint(api, url_prefix='/api')

     

@app.before_request
def lang():
    if request.method == 'GET': 
        if request.args.get('lang') is not None and request.args.get('lang') != '':
            current_user.locale = request.args.get('lang') 

@app.route('/')
def index():
    news = db.session.query(News).all()
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
        user = rfk.User.get_user(db.session, username=username)
        if user and user.check_password(db.session, password=request.form['password']):
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