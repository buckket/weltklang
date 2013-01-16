
class KeyInvalidException(Exception):
    pass

class KeyDisabledException(Exception):
    pass

class FastQueryException(Exception):
    
    def __init__(self, last_access=None):
        self.last_access = last_access
