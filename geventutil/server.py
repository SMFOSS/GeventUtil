from gevent import monkey
monkey.patch_all()

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
logger = logging.getLogger('monkeylib.servers')


def gevent_factory(global_conf, host, port,  **kw):
    """
    Paste factory for gevent

    backlog=None, spawn='default', log='default',
    """
    bl = kw.get('backlog', None)
    if bl is not None:
        kw['backlog'] = int(kw['backlog'])

    spawn = kw.get('spawn', None)
    if spawn is not None:
        try:
            kw['spawn'] = int(spawn)
        except ValueError:
            pass

    origkw = kw.copy()
    graceful = asbool(kw.pop('graceful', False))
    huptimeout = float(kw.pop('huptimeout', 5.5))
    log = kw.pop('access_log', 'off')

    def run(app):
        server = wsgi.WSGIServer((host, int(port)), app, **kw)
        if log == 'off':
            server.log = None
            
        if graceful is True:
            gevent.signal(signal.SIGHUP, graceful_stop, server=server, huptimeout=huptimeout)

        print "Serving %s at %s:%s w/ additional args:\n%s" %(app.__class__.__name__, host, port, "\n".join(["|  %s: %s" % keyval for keyval in origkw.items()]))
        server.serve_forever()

    return run


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
    """
    def __init__(self, app, suffix='pid'):
        self.app = app
        self.exiting = False
        self.suffix = suffix

    def __call__(self, environ, start_response):
        print "Exiting status: %s" %self.exiting
        if self.exiting and environ['PATH_INFO'].endswith(self.suffix):
            return Response("EXITING")(environ, start_response)
        return self.app(environ, start_response)


def make_exiting(app, global_conf, **kw):
    return Exiting(app)
