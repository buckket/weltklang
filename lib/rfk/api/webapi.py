import rfk


def checkAPIKey():
    params = cherrypy.request.params
    
    if not params.has_key('key'):
        raise cherrypy.InternalRedirect('/api/web/error', 'ecode=401&emessage=No Key')
    key = params['key']
    del params['key']

    if rfk.ApiKey.checkKey(key, cherrypy.request.db):
        return
    else:
        raise cherrypy.InternalRedirect('/api/web/error', 'ecode=401&emessage=Wrong Key')

    
cherrypy.tools.checkAPIKey = cherrypy.Tool('before_handler', checkAPIKey)


class WebAPI(object):
    
    def __init__(self):
        pass
    
    def __wrapper(self, data, ecode=0, emessage=None):
        return {'webapi':{'version':'0.1','codename':'Affenkot'},'error':{'code':ecode,'message':emessage},'data':data}
    
    @cherrypy.expose
    def index(self):
        return "Hallo Welt, dies ist WebAPI"
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def error(self, ecode=0, emessage=None):
        return self.__wrapper(None, ecode, emessage)
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.checkAPIKey()
    def dj(self, name=None, id=None):
        '''
        input: name XOR id
        output: {'dj':{'id':int,'name':str}} or {'dj':null}
        '''
        
        pass
    
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.checkAPIKey()
    def currdj(self):
        '''
        input: null
        output: {'dj':{'id':int,'name':str}} or {'dj':null}
        '''
        
        data = {'dj':{'id':1,'name':'MrLoom'}}
        return self.__wrapper(data)
    
    