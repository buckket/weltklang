# -*- coding: utf-8 -*-
import cherrypy
import os
from cherrypy.process import plugins
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

class Jinja2TemplatePlugin(plugins.SimplePlugin):
    """A WSPBus plugin that manages Jinja2 templates"""

    def __init__(self, bus, env):
        plugins.SimplePlugin.__init__(self, bus)
        self.env = env

    def start(self):
        """
        Called when the engine starts. 
        """
        self.bus.log('Setting up Jinja2 resources')
        self.bus.subscribe("lookup-template", self.get_template)

    def stop(self):
        """
        Called when the engine stops. 
        """
        self.bus.log('Freeing up Mako resources')
        self.bus.unsubscribe("lookup-template", self.get_template)
        self.env = None

    def get_template(self, name):
        """
        Returns Jinja2's template by name.

        Used as follow:
        >>> template = cherrypy.engine.publish('lookup-template', 'index.html').pop()
        """
        return self.env.get_template(name)
    # -*- coding: utf-8 -*-

class Jinja2Tool(cherrypy.Tool):
    def __init__(self):
        cherrypy.Tool.__init__(self, 'before_finalize',
                               self._render,
                               priority=10)
        
    def _render(self, template=None, debug=False):
        """
        Applied once your page handler has been called. It
        looks up the template from the various template directories
        defined in the Jinja2 plugin then renders it with
        whatever dictionary the page handler returned.
        """
        if cherrypy.response.status > 399:
            return

        # retrieve the data returned by the handler
        data = cherrypy.response.body or {}
        template = cherrypy.engine.publish("lookup-template", template).pop()

        if template and isinstance(data, dict):
            cherrypy.response.body = template.render(**data)

            
            

class SAEnginePlugin(plugins.SimplePlugin):
    def __init__(self, bus):
        """
        The plugin is registered to the CherryPy engine and therefore
        is part of the bus (the engine *is* a bus) registery.
 
        We use this plugin to create the SA engine. At the same time,
        when the plugin starts we create the tables into the database
        using the mapped class of the global metadata.
 
        Finally we create a new 'bind' channel that the SA tool
        will use to map a session to the SA engine at request time.
        """
        plugins.SimplePlugin.__init__(self, bus)
        self.sa_engine = None
        self.bus.subscribe("bind", self.bind)
 
    def start(self):
        db_path = os.path.abspath(os.path.join(os.curdir, 'data.db'))
        self.sa_engine = create_engine('sqlite:///%s' % db_path, echo=True)
        '''remove line below'''
 
    def stop(self):
        if self.sa_engine:
            self.sa_engine.dispose()
            self.sa_engine = None
 
    def bind(self, session):
        session.configure(bind=self.sa_engine)
 
class SATool(cherrypy.Tool):
    def __init__(self):
        """
        The SA tool is responsible for associating a SA session
        to the SA engine and attaching it to the current request.
        Since we are running in a multithreaded application,
        we use the scoped_session that will create a session
        on a per thread basis so that you don't worry about
        concurrency on the session object itself.

        This tools binds a session to the engine each time
        a requests starts and commits/rollbacks whenever
        the request terminates.
        """
        cherrypy.Tool.__init__(self, 'on_start_resource',
                               self.bind_session,
                               priority=20)

        self.session = scoped_session(sessionmaker(autoflush=True,
                                                  autocommit=False))

    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('on_end_resource',
                                      self.commit_transaction,
                                      priority=80)

    def bind_session(self):
        cherrypy.engine.publish('bind', self.session)
        cherrypy.request.db = self.session

    def commit_transaction(self):
        cherrypy.request.db = None
        try:
            self.session.commit()
        except:
            self.session.rollback()  
            raise
        finally:
            self.session.remove()
