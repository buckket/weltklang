import telnetlib

class LiquidInterface:
    
    timeout = 5000
    
    def __init__(self, host='127.0.0.1', port=1234):
        self.host = host
        self.port = port
        
    def connect(self):
        self.conn = telnetlib.Telnet(self.host, self.port)

    def close(self):
        self.conn.close()
        
    def getSinks(self):
        return self._list(filter='input')
    
    def getSources(self):
        return self._list(filter='input')
    
    def getVersion(self):
        return self._executeCommand('version')
        
    def _list(self,filter=None):
        list = self._executeCommand('list')
        for line in list.splitlines():
            print line
    
    
    def _executeCommand(self, command):
        self.conn.write("%s\n" % command)
        ret = self.conn.read_until('END', self.timeout)
        return ret
    
li = LiquidInterface();
li.connect()
print li._list()
li.close()