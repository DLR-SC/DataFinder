#
# Created: 20.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: configuration.py 3880 2009-03-25 17:22:09Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Defines configuration parameters for the file system implementation.
"""


__version__ = "$LastChangedRevision: 3880 $"


class Configuration(object):
    """ Defines the configuration parameters. """
    
    def __init__(self, baseConfiguration):
        """ 
        Constructor.
        
        @param baseConfiguration: General basic configuration.
        @type baseConfiguration: L{BaseConfiguration<datafinder.persistence.common.configuration.BaseConfiguration>}
        """
        
        self.connectBaseDirectory = False
        if not baseConfiguration.uriHostname is None: # Transforming base URI into an UNC
            self.connectBaseDirectory = True
            self.basePath = "\\\\" + baseConfiguration.uriHostname + "\\"
            if baseConfiguration.uriPath.startswith("/"):
                self.basePath += baseConfiguration.uriPath[1:]
            else:
                self.basePath += baseConfiguration.uriPath
        
        self.basePath = baseConfiguration.uriPath
        self.username = baseConfiguration.username
        self.password = baseConfiguration.password
