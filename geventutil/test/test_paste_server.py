from mock import Mock
from mock import patch
from webob.dec import wsgify
import unittest


@wsgify
def hello_app(request):
    return request.ResponseClass(body='HELLO')


class TestGSF(unittest.TestCase):
    def makeone(self, *args, **kw):
        from geventutil import server
        return server.GeventServerFactory(*args, **kw)
    
    def test_init(self):
        gsf = self.makeone({}, 'localhost', 8080, spawn='1000', backlog='20', graceful='true', huptimeout='0.1', access_log='on')
        assert gsf.additional_args['spawn'] == 1000
        assert gsf.additional_args['backlog'] == 20
        assert gsf.huptimeout == 0.1
        assert gsf.graceful == True
        
    def test_make_server(self):
        gsf = self.makeone({}, 'localhost', 8080, spawn='1000', backlog='20', graceful='true', huptimeout='0.1', access_log='on')
        server = gsf.make_server(hello_app)
        assert server.started is False
        assert server.address == ('localhost', 8080)

    def test_appname(self):
        gsf = self.makeone({}, 'localhost', 8080)
        assert gsf.app_name(hello_app) == 'wsgify', gsf.app_name(hello_app)
        name = hello_app.__name__ = 'Howdy'
        assert gsf.app_name(hello_app) == name, gsf.app_name(hello_app)
    
    def test_noncoercable_spawn_value(self):
        gsf = self.makeone({}, 'localhost', 8080, spawn='raw')
        server = gsf.make_server(hello_app)
        assert server.pool is None

    @patch('geventutil.server.GeventServerFactory.make_server')
    def test_run(self, ms):
        server = ms.return_value = Mock(name='server')
        gsf = self.makeone({}, 'localhost', 8080)
        with gsf.run(hello_app):
            pass
        assert ms.called
        assert repr(server.mock_calls[0]) == 'call.serve_forever()'

    @patch('geventutil.server.GeventServerFactory.make_server')
    def test_call(self, ms):
        server = ms.return_value = Mock(name='server')
        gsf = self.makeone({}, 'localhost', 8080)
        gsf(hello_app)
        assert ms.called
        assert repr(server.mock_calls[0]) == 'call.serve_forever()'
