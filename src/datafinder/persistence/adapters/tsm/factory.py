# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#met:
#
# * Redistributions of source code must retain the above copyright 
#   notice, this list of conditions and the following disclaimer. 
#
# * Redistributions in binary form must reproduce the above copyright 
#   notice, this list of conditions and the following disclaimer in the 
#   documentation and/or other materials provided with the 
#   distribution. 
#
# * Neither the name of the German Aerospace Center nor the names of
#   its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
#OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
#LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
#THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  


""" 
Implements factory for the TSM adapters.
"""


from datafinder.persistence.adapters.tsm import constants
from datafinder.persistence.adapters.tsm.configuration import Configuration
from datafinder.persistence.adapters.tsm.connection_pool import TsmConnectionPool
from datafinder.persistence.adapters.tsm.data.adapter import DataTsmAdapter
from datafinder.persistence.common.base_factory import BaseFileSystem
from datafinder.persistence.common.connection.manager import ConnectionPoolManager


__version__ = "$Revision-Id:$" 


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
