from flask import Flask, session, g, render_template
from flask_sqlalchemy import SQLAlchemy
import rfk
from . import helper

app = Flask(__name__, template_folder='/home/teddydestodes/src/PyRfK/var/template/',
                      static_folder='/home/teddydestodes/src/PyRfK/web_static/',
                      static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = "%s://%s:%s@%s/%s?charset=utf8" % (rfk.config.get('database', 'engine'),
                                                              rfk.config.get('database', 'username'),
                                                              rfk.config.get('database', 'password'),
                                                              rfk.config.get('database', 'host'),
                                                              rfk.config.get('database', 'database'))
app.config['DEBUG'] = True

app.jinja_env.globals['nowPlaying'] = helper.nowPlaying
app.jinja_env.filters['bbcode'] = helper.bbcode
app.jinja_env.filters['timedelta'] = helper.timedelta

db = SQLAlchemy(app)
db.Model = rfk.Base
from . import user
app.register_blueprint(user.user, url_prefix='/user')
@app.route('/')
def index():
    news = db.session.query(rfk.News).all()
    print app.template_folder
    return render_template('index.html', news=news)