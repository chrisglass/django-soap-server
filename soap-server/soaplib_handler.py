#-*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpResponse
from soaplib.wsgi import Application
    
# the class which acts as a wrapper between soaplib WSGI functionality and Django
class DjangoSoapApp(Application):
    '''
    This is a wrapper around the soaplib WSGI interface to make it play nice
    with Django (basically we pretend Django is a WSGI server here)
    '''
    def __call__(self, request):
        django_response = HttpResponse() # This is the actual return value
        
        # Enforce HTTPS
        if not request.is_secure() and not settings.DEBUG: # pragma: nocover 
            django_response.status_code = 400 # Bad request - we need https
            return django_response
        
        # Enforce basic auth
        if not 'HTTP_AUTHORIZATION' in request.META:
            realm = getattr(settings, 'SOAP_SERVER_REALM', 'Webservice')
            django_response.status_code = 401 # Request auth
            django_response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
            return django_response
        
        # The start_response method we'll pass to WSGI
        def start_response(status, headers): # Conforming to WSGI
            status, _ = status.split(' ', 1)
            django_response.status_code = int(status)
            for header, value in headers: # Headers forwarding
                django_response[header] = value
                
        # Now actually call soaplib, do the soap thing
        response = super(DjangoSoapApp, self).__call__(request.META, start_response)
        
        # It returns an iterable of results (as per WSGI specifications)
        # Let's return a more normal django response.
        django_response.content = '\n'.join(response)
        
        return django_response

