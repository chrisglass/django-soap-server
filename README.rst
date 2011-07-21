Django SOAP server
###################


The goal of this projecct is to provide an example of best practices on how to
write a SOAP 1.1 compliant server using Django.

Why using django? Well, while I would really *not* recommend using django for a
pure SOAP webserver (many other solutions would seem far more appropriate),
this project would certainly come in quite handy to people who built a django
website, but want to expose some of its functionality to the world.

REST is all the rage theses days, but you might need this to interface with
legacy products, for example.

How to
=======

# Add soap-server to your INSTALLED_APPS.
# Subclass soap-server.webservice.WebService or soaplib.core.service.DefinitionBase
# 


