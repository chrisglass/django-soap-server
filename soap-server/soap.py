#-*- coding: utf-8 -*-
# soap.py

from .wsgi import embed_wsgi
from django.core import signals
from soaplib.core.server.wsgi import Application as SoaplibWsgiApplication
from soaplib.core import Application as SoaplibApplication


class ExposedWsgiApplication(SoaplibWsgiApplication):
    """Wrapper around soalib.server.wsgi.Application, handling django signals.

    This will send django signals when a SOAP request (apart from retrieving
    the WSDL) is received.

    It should only be used outside of django contexts, since it adds
    request_started/request_finished signals which are already generated in
    other parts of django for django view.
    """

    def on_wsgi_call(self, environ):
        """Called by soaplib code when a SOAP request has just been received."""
        signals.request_started.send(sender=self.__class__)

    def on_wsgi_return(self, environ, http_headers, return_str):
        """Called by soaplib code when a SOAP response is ready for return."""
        # Force charset into Content-Type header, since .Net defaults to latin1.
        http_headers['Content-Type'] = 'text/xml; charset=utf-8'
        signals.request_finished.send(sender=self.__class__)


class Application(SoaplibApplication):
    """Wrapper around a soaplib.core.Application."""

    def as_django_view(self):
        """Return a new Django view embedding this Application."""
        return embed_wsgi(SoaplibWsgiApplication(self))

    def as_wsgi(self):
        """Return a new WSGI Application embedding this Application.

        The WSGI Handler will add django signals on requests in order to behave
        properly with the DB.
        """
        return ExposedWsgiApplication(self)