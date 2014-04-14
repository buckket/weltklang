__author__ = 'teddydestodes'

from bitcoinrpc.authproxy import AuthServiceProxy

from rfk import CONFIG


def get_serviceproxy():
    ap = AuthServiceProxy('http://{username}:{password}@{host}:{port}/'.format(username=CONFIG.get('armord', 'username'),
                                                                               password=CONFIG.get('armord', 'password'),
                                                                               host=CONFIG.get('armord', 'host'),
                                                                               port=CONFIG.get('armord', 'port')))
    return ap