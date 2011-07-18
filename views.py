#-*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from soaplib_handler import DjangoSoapApp
from webservice import WebService

'''
Since the list of applications will end up in the same namespace, make sure you 
don't have two types or methods called the same!

Notice how we must wrap the resulting view in a csrf_exempt() call? 
This is absolutely necessary since it would otherwise diverge from the RFC and 
thus would require custom webservice clients. 
'''

webservice = csrf_exempt(DjangoSoapApp([ # A list of services to expose
                                                 # The are *not* namespaced!
                                                 WebService,
                                                 ], 'ws', name='ws'))
