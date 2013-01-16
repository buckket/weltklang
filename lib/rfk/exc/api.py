'''
Created on Jan 16, 2013

@author: teddydestodes
'''

class KeyInvalidException(Exception):
    pass

class KeyDisabledException(Exception):
    pass

class FastQueryException(Exception):
    
    def __init__(self, lastaccess=None):
        self.lastaccess = lastaccess