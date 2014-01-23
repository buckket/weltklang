from flask import Blueprint, render_template, request, jsonify

from rfk.database.base import User
from rfk.database import session

register = Blueprint('register', __name__)


@register.route('/register', methods=['POST', 'GET'])
def form():
    return render_template("register.html")


@register.route('/register/check', methods=['POST'])
def check():
    ret = {}
    try:
        if User.get_user(username=request.form['username']) == None:
            ret['username'] = 'ok'
        else:
            ret['username'] = 'taken'
    except KeyError:
        pass
    response = jsonify(ret)
    response.status_code = 200
    return response


@register.route('/register/finish', methods=['POST'])
def finish():
    ret = {'success': False}
    try:
        if not User.check_username(request.form['username']):
            ret['username'] = 'invalid'
        elif len(request.form['password']) == 0:
            ret['password'] = 'invalid'
        elif len(request.form['stream_password']) == 0:
            ret['stream_password'] = 'invalid'
        elif User.get_user(username=request.form['username']) == None:
            ret['success'] = True
            user = User(request.form['username'],
                        User.make_password(request.form['password']),
                        User.make_password(request.form['stream_password']))
            session.add(user)
            session.commit()
        else:
            ret['username'] = 'taken'
    except KeyError:
        pass
    response = jsonify(ret)
    response.status_code = 200
    return response


@register.route('/register/success')
def success():
    return render_template("register_success.html")
