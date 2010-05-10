#
# Created: 17.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: configuration.py 3880 2009-03-25 17:22:09Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Defines the set of LDAP-specific configuration parameters.
"""


__version__ = "$LastChangedRevision: 3880 $"


_LDAP_SERVER_DEFAULT_ENCODING = "UTF-8"


class Configuration(object):
    """ Defines a set of configuration parameters of the WebDAV protocol. """
    
    def __init__(self, baseConfiguration):
        """
        Constructor.
        
        @param baseConfiguration: General basic configuration.
        @type baseConfiguration: L{BaseConfiguration<datafinder.persistence.common.configuration.BaseConfiguration>}
        """
        
        self.serverUri = baseConfiguration.baseUri
        self.username = baseConfiguration.username
        self.password = baseConfiguration.password
        self.encoding = baseConfiguration.encoding or _LDAP_SERVER_DEFAULT_ENCODING
        self.baseDn = baseConfiguration.baseDn or ""
        self.domain = baseConfiguration.domain or ""
