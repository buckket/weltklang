'''
Created on 04.05.2012

@author: teddydestodes
'''
import rfk
import rfk.database
from rfk.database.base import User, Permission, UserPermission
import os

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rfk.init(current_dir)
    rfk.database.init_db("%s://%s:%s@%s/%s?charset=utf8" % (rfk.CONFIG.get('database', 'engine'),
                                                              rfk.CONFIG.get('database', 'username'),
                                                              rfk.CONFIG.get('database', 'password'),
                                                              rfk.CONFIG.get('database', 'host'),
                                                              rfk.CONFIG.get('database', 'database')))
    
    rfk.database.session.add(User.add_user('teddydestodes', 'testo'))
    rfk.database.session.commit()
    user = User.query.first()
    permission = Permission.add_permission('admin', 'Admin')
    user.add_permission(permission=permission)
    rfk.database.session.commit()