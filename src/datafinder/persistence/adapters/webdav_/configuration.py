#
# Created: 30.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: configuration.py 3880 2009-03-25 17:22:09Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Defines WebDAV-specific connection parameters. 
"""


__version__ = "$LastChangedRevision: 3880 $"


class Configuration(object):
    """ Defines a set of configuration parameters of the WebDAV protocol. """
    
    def __init__(self, baseConfiguration):
        """ 
        Constructor.
        
        @param baseConfiguration: General basic configuration.
        @type baseConfiguration: L{BaseConfiguration<datafinder.persistence.common.configuration.BaseConfiguration>}
        """
        
        self.baseUrl = baseConfiguration.baseUri
        self.protocol = baseConfiguration.uriScheme
        self.hostname = baseConfiguration.uriHostname or ""
        self.port = baseConfiguration.uriPort
        self.basePath = baseConfiguration.uriPath
        self.username = baseConfiguration.username
        self.password = baseConfiguration.password
        self.userCollectionUrl = baseConfiguration.userCollectionUrl
        self.groupCollectionUrl = baseConfiguration.groupCollectionUrl
