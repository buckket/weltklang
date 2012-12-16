from xml.dom.minidom import Document

class IcecastConfig(object):
    
    def __init__(self):
        self.maxclients = 100
        self.sources = 5
        self.queue_size = 524288
        self.workers = 1
        
        self.client_timeout = 30
        self.header_timeout = 15
        self.source_timeout = 10
        
        self.burst_size = 65536
        
        self.hostname = 'localhost'
        self.address = '127.0.0.1'
        self.port = 8000
        
        self.admin = 'admin'
        self.password = 'hackme'
        self.mounts = []
        
        self.chroot = False
        self.cr_user = 'nobody'
        self.cr_group = 'nogroup'
        
        self.logdir = '/tmp/'
        self.acc_log = 'access.log'
        self.err_log = 'error.log'
        self.loglevel = 2
        self.logarchive = False
        self.logsize = 10000
        
        self.basedir = '/usr/local/share/icecast'
        self.webroot = '/usr/local/share/icecast/web'
        self.adminroot = '/usr/local/share/icecast/admin'
        
        self.master = None
        self.master_port = 8000
        self.update_interval = 120
        self.master_password = 'hackme'
        self.master_user = 'hackme'
        
        self.relay_user = None
        self.relay_password = 'hackme'
        
    def get_xml(self):
        doc = Document()
        conf = doc.createElement('icecast')
        doc.appendChild(conf)
        conf.appendChild(self._put_limits(doc))
        conf.appendChild(self._put_auth(doc))
        hostname = doc.createElement('hostname')
        hostname.appendChild(doc.createTextNode(self.hostname))
        conf.appendChild(hostname)
        conf.appendChild(self._put_listen(doc))
        conf.appendChild(self._put_security(doc))
        conf.appendChild(self._put_paths(doc))
        conf.appendChild(self._put_logging(doc))
        if self.master:
            conf.appendChild(self._put_master(doc))
        for mount in self.mounts:
            conf.appendChild(self._put_mount(doc, mount))
        return doc.toprettyxml('    ')
    
    def _put_limits(self, doc):
        limits = doc.createElement('limits')
        clients = doc.createElement('clients')
        clients.appendChild(doc.createTextNode(str(self.maxclients)))
        sources = doc.createElement('sources')
        sources.appendChild(doc.createTextNode(str(self.sources)))
        client_timeout = doc.createElement('client-timeout')
        client_timeout.appendChild(doc.createTextNode(str(self.client_timeout)))
        header_timeout = doc.createElement('header-timeout')
        header_timeout.appendChild(doc.createTextNode(str(self.header_timeout)))
        source_timeout = doc.createElement('source-timeout')
        source_timeout.appendChild(doc.createTextNode(str(self.source_timeout)))
        burst = doc.createElement('burst-size')
        burst.appendChild(doc.createTextNode(str(self.burst_size)))
        workers = doc.createElement('workers')
        workers.appendChild(doc.createTextNode(str(self.workers)))
        limits.appendChild(clients)
        limits.appendChild(sources)
        limits.appendChild(client_timeout)
        limits.appendChild(header_timeout)
        limits.appendChild(source_timeout)
        limits.appendChild(burst)
        limits.appendChild(workers)
        return limits
    
    def _put_auth(self, doc):
        auth = doc.createElement('authentication')
        admin_user = doc.createElement('admin-user')
        admin_user.appendChild(doc.createTextNode(self.admin))
        admin_pass = doc.createElement('admin-password')
        admin_pass.appendChild(doc.createTextNode(self.password))
        if self.relay_user:
            relay_user = doc.createElement('relay-user')
            relay_user.appendChild(doc.createTextNode(self.relay_user))
            relay_password = doc.createElement('relay-password')
            relay_password.appendChild(doc.createTextNode(self.relay_password))
            auth.appendChild(relay_user)
            auth.appendChild(relay_password)
        auth.appendChild(admin_user)
        auth.appendChild(admin_pass)
        return auth
    
    def _put_listen(self, doc):
        listen = doc.createElement('listen-socket')
        listen_port = doc.createElement('port')
        listen_port.appendChild(doc.createTextNode(str(self.port)))
        listen_address = doc.createElement('bind-address')
        listen_address.appendChild(doc.createTextNode(self.address))
        listen.appendChild(listen_port)
        listen.appendChild(listen_address)
        return listen
    
    def _put_security(self, doc):
        security = doc.createElement('security')
        chroot = doc.createElement('chroot')
        chroot.appendChild(doc.createTextNode(str(int(self.chroot))))
        security.appendChild(chroot)
        if self.chroot:
            changeowner = doc.createElement('changeowner')
            user = doc.createElement('user')
            user.appendChild(doc.createTextNode(self.cr_user))
            group = doc.createElement('group')
            group.appendChild(doc.createTextNode(self.cr_group))
            changeowner.appendChild(user)
            changeowner.appendChild(group)
            security.appendChild(changeowner)
        return security
    
    def _put_paths(self, doc):
        paths = doc.createElement('paths')
        basedir = doc.createElement('basedir')
        basedir.appendChild(doc.createTextNode(self.basedir))
        logdir = doc.createElement('logdir')
        logdir.appendChild(doc.createTextNode(self.logdir))
        webroot = doc.createElement('webroot')
        webroot.appendChild(doc.createTextNode(self.webroot))
        adminroot = doc.createElement('adminroot')
        adminroot.appendChild(doc.createTextNode(self.adminroot))
        alias = doc.createElement('alias')
        alias.setAttribute('source', '/')
        alias.setAttribute('dest', '/status.xsl')
        paths.appendChild(basedir)
        paths.appendChild(logdir)
        paths.appendChild(webroot)
        paths.appendChild(adminroot)
        paths.appendChild(alias)
        return paths
    
    def _put_logging(self, doc):
        logging = doc.createElement('logging')
        access = doc.createElement('accesslog')
        access.appendChild(doc.createTextNode(self.acc_log))
        error = doc.createElement('errorlog')
        error.appendChild(doc.createTextNode(self.err_log))
        loglevel = doc.createElement('loglevel')
        loglevel.appendChild(doc.createTextNode(str(self.loglevel)))
        logsize = doc.createElement('logsize')
        logsize.appendChild(doc.createTextNode(str(self.logsize)))
        logarchive = doc.createElement('logarchive')
        logarchive.appendChild(doc.createTextNode(str(int(self.logarchive))))
        logging.appendChild(access)
        logging.appendChild(error)
        logging.appendChild(loglevel)
        logging.appendChild(logsize)
        logging.appendChild(logarchive)
        return logging
    
    def _put_mount(self, doc, mount):
        mnt = doc.createElement('mount')
        mount_name = doc.createElement('mount-name')
        mount_name.appendChild(doc.createTextNode(mount.mount))
        username = doc.createElement('username')
        username.appendChild(doc.createTextNode(mount.username))
        password = doc.createElement('password')
        password.appendChild(doc.createTextNode(mount.password))
        mnt.appendChild(mount_name)
        #mnt.appendChild(username)
        #mnt.appendChild(password)
        auth = doc.createElement('authentication')
        auth.setAttribute('type','url')
        auth.appendChild(self._gen_auth_option(doc, 'stream_auth', mount.api_url+'auth'))
        auth.appendChild(self._gen_auth_option(doc, 'mount_add', mount.api_url+'add'))
        auth.appendChild(self._gen_auth_option(doc, 'mount_remove', mount.api_url+'remove'))
        auth.appendChild(self._gen_auth_option(doc, 'listener_add', mount.api_url+'listeneradd'))
        auth.appendChild(self._gen_auth_option(doc, 'listener_remove', mount.api_url+'listenerremove'))
        auth.appendChild(self._gen_auth_option(doc, 'username', mount.username))
        auth.appendChild(self._gen_auth_option(doc, 'password', mount.password))
        auth.appendChild(self._gen_auth_option(doc, 'auth_header', 'icecast-auth-user: 1'))
        mnt.appendChild(auth)
        return mnt
    
    def _gen_auth_option(self, doc, name, value):
        option = doc.createElement('option')
        option.setAttribute('name', name)
        option.setAttribute('value', value)
        return option
    
    def _put_master(self,doc):
        master = doc.createElement('master')
        server = doc.createElement('server')
        server.appendChild(doc.createTextNode(self.master))
        port = doc.createElement('port')
        port.appendChild(doc.createTextNode(str(self.master_port)))
        username = doc.createElement('username')
        username.appendChild(doc.createTextNode(self.master_user))
        password = doc.createElement('password')
        password.appendChild(doc.createTextNode(self.master_password))
        interval = doc.createElement('interval')
        interval.appendChild(doc.createTextNode(str(self.update_interval)))
        master.appendChild(server)
        master.appendChild(port)
        master.appendChild(username)
        master.appendChild(password)
        master.appendChild(interval)
        return master
    
    
class Mount(object):
    
    def __init__(self):
        self.mount = ''
        
        self.hidden = False
        
        self.username = 'hackme'
        self.password = 'hackme'
        
        self.api_url = 'http://localhost:8000/backend/icecast/'
        