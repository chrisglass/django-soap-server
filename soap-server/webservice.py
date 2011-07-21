from soaplib.core.service import DefinitionBase, soap
from soaplib.core.model.primitive import String

class WebService(DefinitionBase):
    '''
    The actual webservice class.
    This defines methods exposed to clients.
    '''
    def __init__(self, environ):
        '''
        This saves a reference to the request environment on the current instance
        '''
        self.environ = environ
        super(WebService, self).__init__(environ)

    @soap(String, _returns=String)# Soap is typed - we need stuff like this
    def hello_soap_world(self, name):
        return "Hello, %s!" % name
