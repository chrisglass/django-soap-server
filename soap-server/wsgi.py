#-*- coding: utf-8 -*-
# wsgi.py

"""Embed WSGI applications within Django projects.

An instance of `WSGIHandler` is an "application object" as defined in PEP 3333.
The recommended way to deploy a Django project as a WSGI application is::

    # django.wsgi

    application = django.core.handlers.wsgi.WSGIHandler()

The point of this module is to provide the opposite: deploy a WSGI application
in a Django project. This can be achieved either with a view wrapper or with a
middleware.

The view wrapper provides a straightforward integration in the URLconf::

    # urls.py

    from django.conf.urls.defaults import patterns, url
    from wsgiutil import embed_wsgi

    urlpatterns = patterns('',
        url(r'^my_wsgi_app(/.*)', embed_wsgi('my_wsgi_app.wsgi_callable')),
    )

`embed_wsgi` accepts either a WSGI callable or a path to the callable.

If `django.middleware.csrf.CsrfViewMiddleware` is enabled, you must wrap
`embed_wsgi` in `django.views.decorators.csrf.csrf_exempt`.

WSGI inherits from CGI the concepts of "path to the application object"
(`SCRIPT_NAME`) and "path within the application object" (`PATH_INFO`).
`SCRIPT_NAME` is defined by the first capture in the URL, if there is one, and
`PATH_INFO` is adjusted accordingly.

This setup does not provide a transparent integration, because Django will run
the middlewares. `django.middleware.csrf.CsrfViewMiddleware` will reject all
POST requests by default.

Using `EmbedWsgiMiddleware` to dispatch requests to the WSGI application gives
control on which middlewares will run, but it requires moving some routing
information outside of the URLconf::

    # settings.py

    MIDDLEWARE_CLASSES = (
        'wsgiutil.EmbedWsgiMiddleware',
        ...
    )

    EMBED_WSGI_URLS = (
        ('my_wsgi_app', 'my_wsgi_app.wsgi_callable'),
        ...
    )

The prefix in `EMBED_WSGI_URLS` is appended to `SCRIPT_NAME`, and `PATH_INFO`
is adjusted accordingly.

We will assume that Django is deployed with `WSGIHandler`, which means that
views receive instances of `WSGIRequest`, and that Django's implementation of
WSGI is PEP 3333 compliant. If that is not true, that is a bug in Django, and
this module will not attempt to fix it. Still, it will not a PEP 3333 compliant
WSGI gateway, because Django will always buffer the response.

`validate_wsgi` is an alternative for `embed_wsgi` that will raise errors on
violations of the WSGI specification.
"""


from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, MiddlewareNotUsed
from django.http import HttpResponse
from django.utils.importlib import import_module
from wsgiref.validate import validator



class EmbedWsgiMiddleware(object):

    def __init__(self):
        try:
            embed_wsgi_urls = settings.EMBED_WSGI_URLS
        except AttributeError:
            raise ImproperlyConfigured('You must specify EMBED_WSGI_URLS in '
                                       'your settings file to use '
                                       'EmbedWsgiMiddleware.')
        if not embed_wsgi_urls:
            raise MiddlewareNotUsed('EMBED_WSGI_URLS is emtpy.')
        self.apps = {}
        for prefix, application in embed_wsgi_urls:
            self.apps['/' + prefix] = embed_wsgi(application)

    def process_request(self, request):
        for prefix, view in self.apps.iteritems():
            if request.path.startswith(prefix):
                shift_path(request.environ, prefix)
                return view(request)


def embed_wsgi(application):

    application = load_application(application)

    def view(request, *args, **kwargs):
        response = HttpResponse()

        # Enforce HTTPS if required
        if getattr(settings, 'SOAP_SERVER_HTTPS', True): #pragma: nocover
            if not request.is_secure() and not settings.DEBUG: # pragma: nocover 
                response.status_code = 400 # Bad request - we need https
                return response
        
        # Enforce basic auth
        if hasattr(settings, 'SOAP_SERVER_BASICAUTH_REALM'):
            if not 'HTTP_AUTHORIZATION' in request.environ:
                realm = getattr(settings, 'SOAP_SERVER_BASICAUTH_REALM', 'Webservice')
                response.status_code = 401 # Request auth
                response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
                return response

        # request.environ and request.META are the same object, so changes
        # to the headers by middlewares will be seen here.
        environ = request.environ.copy()
        if len(args) > 0:
            shift_path(environ, '/' + args[0])
        # Django converts SCRIPT_NAME and PATH_INFO to unicode in WSGIRequest.
        environ['SCRIPT_NAME'] = environ.get('SCRIPT_NAME', '').encode('iso-8859-1')
        environ['PATH_INFO'] = environ.get('PATH_INFO', '').encode('iso-8859-1')

        headers_set = []
        headers_sent = []

        def write(data):
            if not headers_set:
                raise AssertionError("write() called before start_response()")
            if not headers_sent:
                # Send headers before the first output.
                for k, v in headers_set:
                    response[k] = v
                headers_sent[:] = [True]
            response.write(data)
            # We could call response.flush() here, but is actually a no-op.

        def start_response(status, headers, exc_info=None):
            # Let Django handle all errors.
            if exc_info:
                raise exc_info[1].with_traceback(exc_info[2])
            if headers_set:
                raise AssertionError("start_response() called again "
                                     "without exc_info")
            response.status_code = int(status.split(' ', 1)[0])
            headers_set[:] = headers
            # Django provides no way to set the reason phrase (#12747).
            return write

        result = application(environ, start_response)
        try:
            for data in result:
                if data:
                    write(data)
            if not headers_sent:
                write('')
        finally:
            if hasattr(result, 'close'):
                result.close()

        return response

    return view


def load_application(application):
    if isinstance(application, basestring):
        app_module, app_name = application.rsplit('.', 1)
        application = getattr(import_module(app_module), app_name)
    if not callable(application):
        raise ImproperlyConfigured('%s isn\'t callable' % application)
    return application


def shift_path(environ, prefix):
    assert environ['PATH_INFO'].startswith(prefix)
    environ['SCRIPT_NAME'] += prefix
    environ['PATH_INFO'] = environ['PATH_INFO'][len(prefix):]


def validate_wsgi(application):
    return validator(embed_wsgi(application))
