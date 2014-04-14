import datetime
from flask import Blueprint, render_template

__author__ = 'teddydestodes'

donation = Blueprint('donation', __name__)

try:
    from rfk.armor import get_serviceproxy
    @donation.route('/list')
    def list():
        sp = get_serviceproxy()
        transactions = []
        for transaction in sp.listtransactions():
            print transaction
            if transaction['category'] != 'recieve': # no one should ever know
                # not comments, need to patch armord to fetch comments and put it into transaction['comment']
                transactions.append({'timestamp': datetime.datetime.fromtimestamp(transaction['time']),
                                     'amount': transaction['amount'],
                                     'currency': 'BTC',
                                     'comment': ''})
        return render_template('donations.html', donations=transactions)

except ImportError:
    @donation.route('/list')
    def list():
        return 'i am sorry;_;'

