# pylint: disable-msg=R0201
# R0201 is disabled in order to correctly implement the interface.
#
# Created: 18.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: factory.py 4626 2010-04-20 20:57:02Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Factory implementation for the standard file system implementation.
"""


from datafinder.persistence.adapters.filesystem.constants import IDENTIFIER_INVALID_CHARACTER_RE, IDENTIFIER_VALID_FIRSTCHARACTER_RE
from datafinder.persistence.adapters.filesystem.configuration import Configuration
from datafinder.persistence.adapters.filesystem.data.adapter import DataFileSystemAdapter
from datafinder.persistence.adapters.filesystem.metadata.adapter import MetadataFileSystemAdapter
from datafinder.persistence.adapters.filesystem.util import ItemIdentifierMapper, connectWindowsShare
from datafinder.persistence.common.base_factory import BaseFileSystem
from datafinder.persistence.error import PersistenceError


__version__ = "$LastChangedRevision: 4626 $"


class FileSystem(BaseFileSystem):
    """ Implements factory method of the different aspects of file system items. """
     
    def __init__(self, baseConfiguration):
        """ 
        Constructor. 
        
        @param configuration: Object specifying the connection parameters.
        L{BaseConfiguration<datafinder.persistence.common.configuration.BaseConfiguration>}
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
    
    def createDataStorer(self, identifier):
        """ 
        Factory Method providing a data storer. 
        """
        
        return DataFileSystemAdapter(identifier, ItemIdentifierMapper(self._configuration.basePath))
    
    def createMetadataStorer(self, identifier):
        """ 
        Factory Method providing a meta data storer. 
        """
        
        return MetadataFileSystemAdapter(identifier, ItemIdentifierMapper(self._configuration.basePath))

    def prepareUsage(self):
        """ Prepares usage of the file system. """
        
        if self._configuration.connectBaseDirectory:
            connectWindowsShare(self._configuration.basePath, self._configuration.username, self._configuration.password)

    def isValidIdentifier(self, name):
        """ 
        This is the WebDAV-specific implementation.
        @see: L{FileSystem.identifierPattern<datafinder.persistence.factory.FileSystem.identifierPattern>}
        """
        
        isValidIdentifer = False, None
        if len(name.strip()) > 0:
            result = IDENTIFIER_INVALID_CHARACTER_RE.search(name)
            if not result is None:
                isValidIdentifer = False, result.start()
            else:
                if IDENTIFIER_VALID_FIRSTCHARACTER_RE.match(name):
                    isValidIdentifer = True, None
                else:
                    isValidIdentifer = False, 0
        return isValidIdentifer
