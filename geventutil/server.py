from gevent import monkey
monkey.patch_all()

from contextlib import contextmanager as cm
from gevent import wsgi
from paste.deploy.converters import asbool
from webob import Response
import gevent
import logging
import os
import signal
import sys


sys.setcheckinterval(10000000) # since we don't use threads, internal checks are not required

pid = os.getpid()
logger = logging.getLogger(__name__)


class GeventServerFactory(object):
    server_factory = wsgi.WSGIServer
    def __init__(self, global_conf, host, port, **kwargs):
        self.original_args = kwargs.copy()
        self.global_conf = global_conf
        self.host = host
        self.port = port
        self.graceful = asbool(kwargs.pop('graceful', False))
        self.huptimeout = float(kwargs.pop('huptimeout', 5.5))
        self.log = kwargs.pop('access_log', 'off')
        self._server = None
        self.additional_args = self.prep_args(kwargs)

    def prep_args(self, val):
        bl = val.get('backlog', None)
        if bl is not None:
            val['backlog'] = int(val['backlog'])

        spawn = val.get('spawn', None)
        if spawn is not None:
            try:
                val['spawn'] = int(spawn)
            except ValueError:
                pass
        return val

    def make_server(self, app):
        server = self.server_factory((self.host, int(self.port)), app, **self.additional_args)
        if self.log == 'off':
            server.log = None
            
        if self.graceful is True:
            gevent.signal(signal.SIGHUP, graceful_stop, server=server, huptimeout=self.huptimeout)
        return server

    def app_name(self, app):
        appname = getattr(app, '__app_name__', None)
        name = getattr(app, '__name__', None)
        klass = getattr(app, '__class__', None)
        if not appname is None:
            return appname
        if name is None:
            return klass.__name__
        return name


    def __call__(self, app):
        with self.run(app):
            name = self.app_name(app)
            arguments = "\n".join(["|  %s: %s" % keyval \
                                       for keyval in self.original_args.items()])
            msg = "PID %s serving '%s' at %s:%s w/ additional args:\n%s"\
                %(pid, name, self.host, self.port, arguments)
            rule = "---"
            print
            print rule
            print msg.strip()
            print rule

    @cm
    def run(self, app):
        server = self.make_server(app)
        try:
            yield
        finally:
            server.serve_forever()


def graceful_stop(server=None, huptimeout=None):
    """
    Sighup handler -- attempts to let existing transactions finish
    before close connections
    """
    if isinstance(server.application, Exiting):
        server.application.exiting = True
        logger.info("HUP RECEIVED: EXITING %s in %f", pid, huptimeout)
        if server.pool:
            server.pool.join(timeout=huptimeout)
            server.pool.kill(block=True, timeout=1)
            server.stop_accepting()
            server.pool = False
        server.stop()


class Exiting(object):
    """
    Middleware for indicating we are exiting

    - Must be outer most middleware
    """
    logger = logger
    def __init__(self, app, suffix='pid'):
        self.app = app
        self.exiting = False
        self.suffix = suffix

    def __call__(self, environ, start_response):
        self.logger.debug("Exiting status: %s", self.exiting)
        if self.exiting and environ['PATH_INFO'].endswith(self.suffix):
            return Response("EXITING")(environ, start_response)
        return self.app(environ, start_response)


def make_exiting(app, global_conf, **kw):
    return Exiting(app)
