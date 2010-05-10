#
# Created: 21.09.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: factory.py 4283 2009-09-30 13:34:32Z schlauch $ 
# 
# Copyright (c) 2009, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements factory for the TSM adapters.
"""


from datafinder.persistence.adapters.tsm import constants
from datafinder.persistence.adapters.tsm.configuration import Configuration
from datafinder.persistence.adapters.tsm.connection_pool import TsmConnectionPool
from datafinder.persistence.adapters.tsm.data.adapter import DataTsmAdapter
from datafinder.persistence.common.base_factory import BaseFileSystem
from datafinder.persistence.common.connection.manager import ConnectionPoolManager


__version__ = "$LastChangedRevision: 4283 $"


class FileSystem(BaseFileSystem):
    """ Implements factory of the TSM file system. """
    
    _connectionManager = ConnectionPoolManager(constants.MAX_POOL_NUMBER)
    
    def __init__(self, baseConfiguration):
        """ 
        Constructor. 
        
        @param baseConfiguration: The persistence package common baseConfiguration class.
        @type baseConfiguration: L{BaseConfiguration<datafinder.persistence.common.BaseConfiguration>}
        """
        
        BaseFileSystem.__init__(self)
        self._configuration = Configuration(baseConfiguration)
        self._connectionPool = self._getConnectionPool()

    def _getConnectionPool(self):
        """ Creates / retrieves a usable connection pool for the given configuration. """
        
        connectionPool = self._connectionManager.get(self._configuration.baseUri)
        if connectionPool is None:
            connectionPool = TsmConnectionPool(self._configuration)
            self._connectionManager.add(self._configuration.baseUri, connectionPool)
        return connectionPool
    
    def createDataStorer(self, identifier):
        """ 
        Creates a TSM specific data storer instance.
        
        @param identifier: Logical identifier of a file system item.
        @type identifier: C{unicode}
        
        @return: TSM specific data storer instance.
        @rtype: L{DataTsmAdapter<datafinder.persistence.adapters.tsm.adapter.DataTsmAdapter>}
        """
        
        return DataTsmAdapter(identifier, self._determinePeristenceIdentifier(identifier), 
                              self._configuration.serverNodeName, self._connectionPool)
    
    def _determinePeristenceIdentifier(self, identifier):
        """
        Transforms the logical identifier to the persistence identifier.
        """
        
        if identifier.startswith("/"):
            persistenceId = self._configuration.basePath + identifier
        else:
            persistenceId = self._configuration.basePath + "/" + identifier
        return persistenceId

    def release(self):
        """ 
        @see: L{FileSystem.release<datafinder.persistence.factory.FileSystem.release>}
        Cleans up the connection pool
        """
        
        self._connectionPool.reload()

    def updateCredentials(self, credentials):
        """ 
        @see: L{FileSystem.updateCredentials<datafinder.persistence.factory.FileSystem.updateCredentials>} 
        Change the credentials and initializes the the connection pool again.
        """
        
        self._configuration.username = credentials["username"]
        self._configuration.password = credentials["password"]
        self._connectionPool.reload()
