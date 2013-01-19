'''
Created on Jan 18, 2013

@author: teddydestodes
'''
class UserNotFoundException(Exception):
    pass

class InvalidPasswordException(Exception):
    pass

class InvalidSettingException(Exception):
    
    def __init__(self, reason):
        self.reason = reason
        
    def __repr__(self):
        "<rfk.exc.base.InvalidSettingException %s>" % (self.reason,)