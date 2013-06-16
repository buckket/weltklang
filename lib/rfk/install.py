'''
Created on May 31, 2013

@author: teddydestodes
'''

from rfk.database.base import Permission, Setting, User
import rfk.database


def setup_settings():
    settings = []
    settings.append(Setting.add_setting('use_icy', 'Use ICY-Tags for unplanned Shows', Setting.TYPES.INT))
    settings.append(Setting.add_setting('show_def_name', 'Default Name for new Shows', Setting.TYPES.STR))
    settings.append(Setting.add_setting('show_def_desc', 'Default Description for new Shows', Setting.TYPES.STR))
    settings.append(Setting.add_setting('show_def_tags', 'Default Tags for new Shows', Setting.TYPES.STR))
    settings.append(Setting.add_setting('show_def_logo', 'Default Logo for Shows', Setting.TYPES.STR))
    settings.append(Setting.add_setting('locale', 'Locale', Setting.TYPES.STR))
    settings.append(Setting.add_setting('timezone', 'Timezone', Setting.TYPES.STR))
    for setting in settings:
        rfk.database.session.add(setting)
    rfk.database.session.commit() 

def setup_permissions():
    permissions = []
    permissions.append(Permission.add_permission('manage-liquidsoap', 'Manage Liquidsoap'))
    permissions.append(Permission.add_permission('manage-relays', 'Manage Relays'))
    permissions.append(Permission.add_permission('manage-users', 'Manage Users'))
    permissions.append(Permission.add_permission('admin', 'Admin'))
    for permission in permissions:
        rfk.database.session.add(permission)
    rfk.database.session.commit()
    
def setup_default_user(username, password):
    users = []
    users.append(User.add_user(username, password))
    for user in users:
        rfk.database.session.add(user)
        user.add_permission(code='manage-liquidsoap')
        user.add_permission(code='manage-relays')
        user.add_permission(code='admin')
        print "[users] Added %s" % user.username
    rfk.database.session.commit()
    
def setup_statistics():
    stat = rfk.database.stats.Statistic(name="Overall Listener", identifier="lst-total")
    rfk.database.session.add(stat)
    rfk.database.session.commit()