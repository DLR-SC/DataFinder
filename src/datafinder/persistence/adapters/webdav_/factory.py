# pylint: disable-msg=R0201
# R0201 is disabled in order to correctly implement the interface.
#
# Created: 30.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: factory.py 4626 2010-04-20 20:57:02Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements factory methods for objects that can be used to
access a WebDAV file system.
"""


__version__ = "$LastChangedRevision: 4626 $"


from webdav.Connection import WebdavError

from datafinder.persistence.adapters.webdav_.configuration import Configuration
from datafinder.persistence.adapters.webdav_.connection_pool import WebdavConnectionPool
from datafinder.persistence.adapters.webdav_ import constants
from datafinder.persistence.adapters.webdav_.constants import IDENTIFIER_VALID_STARTCHARACTER_RE, \
                                                              IDENTIFIER_INVALID_CHARACTER_RE, \
                                                              PROPERTYNAME_VALID_STARTCHARACTER_RE, \
                                                              PROPERTYNAME_INVALID_CHARACTER_RE
from datafinder.persistence.adapters.webdav_.util import ItemIdentifierMapper, createCollectionStorer
from datafinder.persistence.adapters.webdav_.data.adapter import DataWebdavAdapter
from datafinder.persistence.adapters.webdav_.metadata.adapter import MetadataWebdavAdapter
from datafinder.persistence.adapters.webdav_.principal_search.adapter import PrincipalSearchWebdavAdapter
from datafinder.persistence.adapters.webdav_.privileges.adapter import PrivilegeWebdavAdapter
from datafinder.persistence.adapters.webdav_.privileges.privileges_mapping import PrivilegeMapper
from datafinder.persistence.common.base_factory import BaseFileSystem
from datafinder.persistence.common.connection.manager import ConnectionPoolManager
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.privileges.privilegestorer import NullPrivilegeStorer


class FileSystem(BaseFileSystem):    """ 
    Implements factory methods of the different aspects of file system items. 
    Moreover, information of specific feature are available.
    """
     
    _connectionManager = ConnectionPoolManager(constants.MAX_POOL_NUMBER)

    def __init__(self, baseConfiguration):
        """ 
        Constructor. 
        
        @param baseConfiguration: Object specifying configuration parameters.
        @type baseConfiguration: L{BaseConfiguration<datafinder.persistence.common.configuration.BaseConfiguration>}
        """
        
        BaseFileSystem.__init__(self)
        self._configuration = Configuration(baseConfiguration)
        self._hasMetadataSearchSupport = None
        self._hasPrivilegeSupport = None
        self._resourceTypeCache = dict()
        self._connectionPool = self._getConnectionPool()

    def _getConnectionPool(self):
        """ Creates / retrieves a usable connection pool for the given configuration. """
        
        connectionPool = self._connectionManager.get(self._configuration.baseUrl)
        if connectionPool is None:
            connectionPool = WebdavConnectionPool(self._configuration)
            self._connectionManager.add(self._configuration.baseUrl, connectionPool)
        return connectionPool

    def updateCredentials(self, credentials):
        """ @see: L{updateCredentials<datafinder.persistence.factory.FileSystem.updateCredentials>} """
        
        try:
            self._configuration.username = credentials["username"]
            self._configuration.password = credentials["password"]
        except KeyError:
            raise PersistenceError("Invalid credentials provided.")
        else:
            self._connectionPool.reload()
    
    def createDataStorer(self, identifier):
        """ 
        Factory Method providing a WebDAV-specific data storer. 
        
        @return: WebDAV-specific implementation of the data interface.
        @rtype: L{DataWebdavAdapter<datafinder.persistence.adapters.webdav_.
        data.adapter.DataWebdavAdapter>
        """
        
        return DataWebdavAdapter(identifier, self._connectionPool, 
                                 ItemIdentifierMapper(self._configuration.baseUrl), resourceTypeCache=self._resourceTypeCache)
    
    def createMetadataStorer(self, identifier):
        """ 
        Factory Method providing a WebDAV-specific meta data storer. 
        
        @return: WebDAV-specific implementation of the meta data interface.
        @rtype: L{MetadataWebdavAdapter<datafinder.persistence.adapters.webdav_.
        metadata.adapter.MetadataWebdavAdapter>
        """

        return MetadataWebdavAdapter(identifier, self._connectionPool, ItemIdentifierMapper(self._configuration.baseUrl), 
                                     hasMetadataSearchSupport=self.hasMetadataSearchSupport)
    
    def createPrivilegeStorer(self, identifier):
        """ 
        Factory Method providing a WebDAV-specific privilege storer. 
        
        @return: WebDAV-specific implementation of the privilege interface.
        @rtype: L{PrivilegeWebdavAdapter<datafinder.persistence.adapters.webdav_.
        privileges.adapter.PrivilegeWebdavAdapter>
        """
        
        if self.hasPrivilegeSupport:
            return PrivilegeWebdavAdapter(identifier, self._connectionPool, ItemIdentifierMapper(self._configuration.baseUrl),
                                          PrivilegeMapper(self._configuration.userCollectionUrl, self._configuration.groupCollectionUrl))
        else:
            return NullPrivilegeStorer(identifier)
        
    def createPrincipalSearcher(self):
        """ 
        Factory method for the WebDAV-specific principal search object. 
        
        @return: WebDAV-specific implementation of the principal search interface.
        @rtype: L{PrincipalSearchWebdavAdapter<datafinder.persistence.adapters.webdav_.
        principal_search.adapter.PrincipalSearchWebdavAdapter>
        """
        
        return PrincipalSearchWebdavAdapter(self._configuration.userCollectionUrl, self._configuration.groupCollectionUrl, 
                                            self._connectionPool)

    def release(self):
        """ Releases the acquired connection pool. """
        
        self._connectionManager.remove(self._configuration.baseUrl)

    def isValidIdentifier(self, name):
        """ 
        This is the WebDAV-specific implementation.
        @see: L{FileSystem.identifierPattern<datafinder.persistence.factory.FileSystem.identifierPattern>}
        """
        
        return self._isValidIdentifierHelper(name, IDENTIFIER_INVALID_CHARACTER_RE, IDENTIFIER_VALID_STARTCHARACTER_RE)
    
    @staticmethod
    def _isValidIdentifierHelper(name, invalidCharRe, validStartCharRe):
        """ Helper used for identifier validation. """
        
        isValidIdentifer = False, None
        if len(name.strip()) > 0:
            result = invalidCharRe.search(name)
            if not result is None:
                isValidIdentifer = False, result.start()
            else:
                if validStartCharRe.match(name):
                    isValidIdentifer = True, None
                else:
                    isValidIdentifer = False, 0
        return isValidIdentifer
    
    def isValidMetadataIdentifier(self, name):
        """ 
        This is the WebDAV-specific implementation.
        @see: L{FileSystem.metadataIdentifierPattern<datafinder.persistence.factory.FileSystem.metadataIdentifierPattern>}
        """
        
        return self._isValidIdentifierHelper(name, PROPERTYNAME_INVALID_CHARACTER_RE, PROPERTYNAME_VALID_STARTCHARACTER_RE)
    
    @property #R0201
    def hasCustomMetadataSupport(self):
        """ 
        This is the WebDAV-specific implementation.
        @note: Always returns C{True} because custom meta data support is a built-in WebDAV feature.
        @see: L{FileSystem.hasCustomMetadataSupport<datafinder.persistence.factory.FileSystem.hasCustomMetadataSupport>}
        """
        
        return True
    
    @property #R0201
    def hasMetadataSearchSupport(self):
        """ 
        This is the WebDAV-specific implementation.
        @see: L{FileSystem.hasMetadataSearchSupport<datafinder.persistence.factory.FileSystem.hasMetadataSearchSupport>}
        """
        
        if self._hasMetadataSearchSupport is None:
            
            connection = self._connectionPool.acquire()
            try:
                try:
                    collectionStorer = createCollectionStorer(self._configuration.baseUrl, connection, False)
                    self._hasMetadataSearchSupport = collectionStorer.daslBasicsearchSupportAvailable
                except WebdavError:
                    self._hasMetadataSearchSupport = False
            finally:
                self._connectionPool.release(connection)
        return self._hasMetadataSearchSupport
    
    @property #R0201
    def hasPrivilegeSupport(self):
        """ 
        This is the WebDAV-specific implementation.
        @see: L{FileSystem.hasPrivilegeSupport<datafinder.persistence.factory.FileSystem.hasPrivilegeSupport>}
        """
    
        if self._hasPrivilegeSupport is None:
            connection = self._connectionPool.acquire()
            try:
                try:
                    collectionStorer = createCollectionStorer(self._configuration.baseUrl, connection, False)
                    self._hasPrivilegeSupport = collectionStorer.aclSupportAvailable
                except (WebdavError, AttributeError):
                    self._hasPrivilegeSupport = False
            finally:
                self._connectionPool.release(connection)
        return self._hasPrivilegeSupport
