#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.views.decorators.csrf import csrf_exempt
from webservice import WebService
from soap import Application

'''
Since the list of applications will end up in the same namespace, make sure you 
don't have two types or methods called the same!

Notice how we must wrap the resulting view in a csrf_exempt() call? 
This is absolutely necessary since it would otherwise diverge from the RFC and 
thus would require custom webservice clients. 
'''

# This is just for readability's sake
application_view = Application([WebService], 'ws', name='ws').as_django_view()

urlpatterns = patterns('',
    # That's it. Call this url with "?wsdl" to get the wsdl file
    url(r'^.*', csrf_exempt( application_view ))
    )
