#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from views import webservice


urlpatterns = patterns('',
    # That's it. Call this url with "?wsdl" to get the wsdl file
    url(r'^.*', webservice), # IMPORTANT: do not end regexp with '$' !
)
