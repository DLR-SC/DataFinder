# pylint: disable-msg=R0201, W0613
# R0201 is disabled for provision of a default implementation (static methods).
# W0613 is disabled for provision of a default implementation (unused argument).
#
# Created: 22.09.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: base_factory.py 4626 2010-04-20 20:57:02Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Base class for the adaptor specific file system factory implementations.
"""


from datafinder.persistence.data.datastorer import NullDataStorer
from datafinder.persistence.metadata.metadatastorer import NullMetadataStorer
from datafinder.persistence.principal_search.principalsearcher import NullPrincipalSearcher
from datafinder.persistence.privileges.privilegestorer import NullPrivilegeStorer


__version__ = "$LastChangedRevision: 4626 $"


class BaseFileSystem(object):
    """ Base class for the adaptor specific file system factory implementations. """
    
    def createDataStorer(self, identifier):
        """ 
        Factory method an adapter specific data storer. 
        
        @return: Adapter specific data storer.
        @rtype: instanceOf L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        return NullDataStorer(identifier)
    
    def createMetadataStorer(self, identifier):
        """ 
        Factory method an adapter specific meta data storer. 
        
        @return: Adapter specific meta data storer.
        @rtype: instanceOf L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}
        """
        
        return NullMetadataStorer(identifier)
    
    def createPrivilegeStorer(self, identifier):
        """ 
        Factory method an adapter specific meta data storer. 
        
        @return: Adapter specific meta data storer.
        @rtype: instanceOf L{NullMetadataStorer<datafinder.persistence.privileges.privilegestorer.NullPrivilegeStorer>}
        """
        
        return NullPrivilegeStorer(identifier)
    
    def createPrincipalSearcher(self):
        """ 
        Factory method an adapter specific meta data storer. 
        
        @return: Adapter specific meta data storer.
        @rtype: instanceOf L{NullMetadataStorer<datafinder.persistence.privileges.privilegestorer.NullPrivilegeStorer>}
        """
        
        return NullPrincipalSearcher()

    def release(self):
        """ 
        @see: L{FileSystem.release<datafinder.persistence.factory.FileSystem.release>}
        @note: The default implementation does nothing.
        """
        
        pass

    def updateCredentials(self, credentials):
        """ 
        @see: L{FileSystem.updateCredentials<datafinder.persistence.factory.FileSystem.updateCredentials>} 
        @note: The default implementation does nothing.
        """
        
        pass

    def prepareUsage(self):
        """
        Prepares usage of the file system. 
        @note: The default implementation does nothing.
        """
    
        pass
    
    def isValidIdentifier(self, name): # W0613
        """ 
        @see: L{FileSystem.isValidIdentifier<datafinder.persistence.factory.FileSystem.metadataIdentifierPattern>}
        @note: This implementation always returns C{True}, C{None}.
        """
        
        return True, None

    def isValidMetadataIdentifier(self, name): # W0613
        """ 
        @see: L{FileSystem.metadataIdentifier<datafinder.persistence.factory.FileSystem.metadataIdentifierPattern>}
        @note: This implementation always returns C{True}, C{None}.
        """
        
        return True, None
    
    @property
    def hasCustomMetadataSupport(self):
        """ 
        @see: L{FileSystem.hasCustomMetadataSupport<datafinder.persistence.factory.FileSystem.hasCustomMetadataSupport>}
        @note: This implementation always returns C{False}.
        """
        
        return False
    
    @property
    def hasMetadataSearchSupport(self):
        """ 
        @see: L{FileSystem.hasMetadataSearchSupport<datafinder.persistence.factory.FileSystem.hasMetadataSearchSupport>}
        @note: This implementation always returns C{False}.
        """
        
        return False
    
    @property
    def hasPrivilegeSupport(self):
        """ 
        @see: L{FileSystem.hasPrivilegeSupport<datafinder.persistence.factory.FileSystem.hasPrivilegeSupport>}
        @note: This implementation always returns C{False}.
        """
    
        return False
