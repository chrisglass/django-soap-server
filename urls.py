#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from views import webservice


urlpatterns = patterns('',
    url(r'^service.wsdl$', webservice ), # This is the WSDL
    url(r'^.*', webservice), # IMPORTANT: do not end regexp with '$' !
)
