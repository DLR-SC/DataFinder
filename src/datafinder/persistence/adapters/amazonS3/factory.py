# pylint: disable-msg=R0201, W0511
# R0201 is disabled in order to correctly implement the interface.
#
# Created: 28.11.2009 ney <Miriam.Ney@dlr.de>
# Changed: $Id: factory.py 4559 2010-03-23 15:20:18Z ney_mi $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements factory methods for objects that can be used to
access a Amazon s3 file system.

to be implemented - erstellt einen Datastore des Typs S3
"""


__version__ = "$LastChangedRevision: 4559 $"


from boto.s3.connection import S3Connection 

from datafinder.persistence.adapters.amazonS3.configuration import Configuration
from datafinder.persistence.adapters.amazonS3.connection_pool import S3ConnectionPool
from datafinder.persistence.adapters.amazonS3.data.adapter import DataS3Adapter
from datafinder.persistence.adapters.amazonS3 import constants

from datafinder.persistence.common.base_factory import BaseFileSystem
from datafinder.persistence.common.connection.manager import ConnectionPoolManager
from datafinder.persistence.error import PersistenceError

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
        self._connection = self._getConnection()
        self._connectionPool = self._getConnectionPool()
    

    def _getConnection(self):
        """ Creates / retrieves a usable connection for the given configuration. """
        
        self._connection = S3Connection(self._configuration.awsAccessKey, self._configuration.awsSecretAccessKey)
        
    def _getConnectionPool(self):
        
        connectionPool = self._connectionManager.get(self._configuration.baseUrl)
        if connectionPool is None:
            connectionPool = S3ConnectionPool(self._configuration)
            self._connectionManager.add(self._configuration.baseUrl, connectionPool)
        return connectionPool
    
        
    def updateCredentials(self, credentials):
        """ @see: L{updateCredentials<datafinder.persistence.factory.FileSystem.updateCredentials>} """
        #TODO: correctCredential implementation
        try:
            self._configuration.username = credentials["username"]
            self._configuration.password = credentials["password"]
        except KeyError:
            raise PersistenceError("Invalid credentials provided.")
        else:
            self._connection = self._getConnection()
    
    def createDataStorer(self, identifier):
        """ 
        Factory Method providing a Amazon S3-specific data storer. 
        
        @return: Amazon S3-specific implementation of the data interface.
        @rtype: ... # missing return type
        """
        
        return DataS3Adapter(identifier, self._connection, self._configuration.bucketName, self._configuration.keyName)
    
    def getConnection(self):
        """
        Getter for the Connection
        """
        
        return self._connection
    
  
    def getConfiguration(self):
        """
        Getter for the Configuration 
        """
        
        return self._configuration
    
    def release(self):
        """ Releases the acquired connection pool. """
        
        self._connectionManager.remove(self._configuration.baseUrl)
