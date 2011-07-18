#-*- coding: utf-8 -*-
"""
This file holds all the utils functions and helpers for the webservice.
"""
from django.contrib.auth import authenticate
from django.utils.log import logger
import base64

#===============================================================================
# Helpers
#===============================================================================

def get_user_from_environment(environ):
    '''
    This logs in a Django user from a Basic auth
    '''
    auth = environ.get('HTTP_AUTHORIZATION', None)
    assert auth != None, 'Webservice cannot be called without basic auth!'

    _, based = auth.split(' ') # typical string is 'Basic <b64 encoding>'
    plain_auth = base64.b64decode(based) # has the form '<username>:<password>'
    username, password = plain_auth.split(':')
    user = authenticate(username=username, password=password)
    return user

