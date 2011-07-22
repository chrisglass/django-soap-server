
from django.test.testcases import TestCase
from soap-server.wsgi import embed_wsgi

def simple_wsgi(*args, **kwargs):
    """ A simple webservice for test purposes"""
    return ['']

class SoapLibHandlerTestCase(TestCase):
    
    def test_unsecure_call_returns_a_400(self):
        request = Mock()
        setattr(request, 'is_secure', lambda:False)
        app = embed_wsgi(simple_wsgi)
        res = app(request)
        self.assertEqual(res.status_code, 400)
    
    def test_secure_unauthenticated_call_returns_a_401(self):
        request = Mock()
        setattr(request, 'is_secure', lambda:True)
        setattr(request, 'environ', {})
        app = embed_wsgi(simple_wsgi)
        res = app(request)
        self.assertEqual(res.status_code, 401)
    
    def test_secure_authenticated_call_returns_a_405(self):
        request = Mock()
        setattr(request, 'is_secure', lambda:True)
        setattr(request, 'environ', {})
        app = embed_wsgi(simple_wsgi)
        res = app(request)
        self.assertEqual(res.status_code, 405)
        
    # TODO Make a 200 check
