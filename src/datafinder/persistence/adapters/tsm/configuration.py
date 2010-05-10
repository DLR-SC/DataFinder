#
# Created: 19.08.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: configuration.py 4283 2009-09-30 13:34:32Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements a configuration holder object.
"""


from urlparse import urlsplit


__version__ = "$LastChangedRevision: 4283 $"


class Configuration(object):
    """ Defines a set of configuration parameters for TSdM access. """
    
    def __init__(self, baseConfiguration):
        """ 
        Constructor.
        
        @param baseConfiguration: General basic configuration.
        @type baseConfiguration: L{BaseConfiguration<datafinder.persistence.common.configuration.BaseConfiguration>}
        """
        
        self.baseUri = baseConfiguration.baseUri
        hostname, path = self._determineHostAndPath(baseConfiguration.uriPath or "")
        self.hostname = hostname or ""
        self.basePath = path
        self.username = baseConfiguration.username
        self.password = baseConfiguration.password
        self.serverNodeName = baseConfiguration.serverNodeName
        
    @staticmethod
    def _determineHostAndPath(hostAndPath):
        """ 
        Need to do a little trick because C{tsm} is no standard 
        URI scheme and thus host name and path are not correctly split.
        Just changing the scheme to a supported one.
        """
        
        splitUrl = urlsplit("http:" + hostAndPath)
        return splitUrl.hostname, splitUrl.path
