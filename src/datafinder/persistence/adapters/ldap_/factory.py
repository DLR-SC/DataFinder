#
# Created: 17.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: factory.py 4253 2009-09-24 10:35:14Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
LDAP-specific factory implementation.
"""


from datafinder.persistence.adapters.ldap_.configuration import Configuration
from datafinder.persistence.adapters.ldap_.principal_search.adapter import LdapPrincipalSearchAdapter
from datafinder.persistence.common.base_factory import BaseFileSystem
from datafinder.persistence.error import PersistenceError


__version__ = "$LastChangedRevision: 4253 $"


class FileSystem(BaseFileSystem):
    """ Implements factory method of the different aspects of file system items. """
     
    def __init__(self, baseConfiguration):
        """ 
        Constructor. 
        
        @param baseConfiguration: General basic configuration.
        @type baseConfiguration: L{BaseConfiguration<datafinder.persistence.common.configuration.BaseConfiguration>}
        """
        
        BaseFileSystem.__init__(self)
        self._configuration = Configuration(baseConfiguration)
        
    def updateCredentials(self, credentials):
        """ @see: L{updateCredentials<datafinder.persistence.factory.FileSystem.updateCredentials>} """
        
        try:
            self._configuration.username = credentials["username"]
            self._configuration.password = credentials["password"]
        except KeyError:
            raise PersistenceError("Invalid credentials provided.")
            
    def createPrincipalSearcher(self):
        """ factory method for the principal search object. """
        
        return LdapPrincipalSearchAdapter(self._configuration)
