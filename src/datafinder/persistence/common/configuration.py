#
# Created: 24.03.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: configuration.py 3898 2009-04-01 16:39:50Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Module provides class defining basic configuration parameters.
"""


from urlparse import urlsplit


__version__ = "$LastChangedRevision: 3898 $"


class BaseConfiguration(object):
    """
    Contains the basic configuration parameters for accessing a generic file system.
    Additional configuration parameters can be specified using keyword arguments.
    """
    
    def __init__(self, baseUri=None, **kwargs):
        """ 
        Constructor.
        
        @param baseUri: URI of an item in the file system the other items are addressed relative to.
        @type baseUri: C{unicode}
        """
        
        self._baseUri = None
        self.uriScheme = None
        self.uriNetloc = None
        self.uriHostname = None
        self.uriPort = None
        self.uriPath = None
    
        self.baseUri = baseUri
        self.__dict__.update(kwargs)
        
    def __getBaseUri(self):
        """ Simple getter. """
        
        return self._baseUri
        
    def __setBaseUri(self, baseUri):
        """ Sets the base URI. """
        
        if not baseUri is None:
            parsedUri = urlsplit(baseUri)
            self._baseUri = parsedUri.geturl()
            self.uriScheme = parsedUri.scheme
            self.uriNetloc = parsedUri.netloc
            self.uriHostname = parsedUri.hostname
            try:
                self.uriPort = parsedUri.port
            except ValueError:
                self.uriPort = None
            self.uriPath = parsedUri.path
        
    baseUri = property(__getBaseUri, __setBaseUri)
        
    def __getattr__(self, _):
        """ 
        Returns C{None} for unknown attributes instead of raising an C{AttributeError}. 
        This is provided for convenience to avoid boiler-plate exception handling code.
        """
        
        return None
