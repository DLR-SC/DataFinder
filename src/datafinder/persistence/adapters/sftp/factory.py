#
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
Implements the basic SFTP file system.
"""


from datafinder.persistence.adapters.sftp import constants, utils
from datafinder.persistence.adapters.sftp.configuration import Configuration
from datafinder.persistence.adapters.sftp.connection_pool import SftpConnectionPool
from datafinder.persistence.adapters.sftp.data.adapter import SftpDataAdapter
from datafinder.persistence.common.base_factory import BaseFileSystem
from datafinder.persistence.common.connection.manager import ConnectionPoolManager


__version__ = "$Revision-Id:$" 


class FileSystem(BaseFileSystem):
    """ Implements factory of the SFTP file system. """
    
    _connectionManager = ConnectionPoolManager(constants.MAX_POOL_NUMBER)
    
    def __init__(self, baseConfiguration):
        """ 
        @param baseConfiguration: Configuration parameters.
        @type baseConfiguration: L{BaseConfiguration<datafinder.persistence.common.BaseConfiguration>}
        """
        
        BaseFileSystem.__init__(self)
        self._configuration = Configuration(baseConfiguration)
        self._connectionPool = self._getConnectionPool()
        self._idMapper = utils.ItemIdentifierMapper(self._configuration.basePath)
        
    def _getConnectionPool(self):
        connectionPool = self._connectionManager.get(self._configuration.baseUri)
        if connectionPool is None:
            connectionPool = SftpConnectionPool(self._configuration)
            self._connectionManager.add(self._configuration.baseUri, connectionPool)
        return connectionPool
    
    def createDataStorer(self, identifier):
        """ 
        Creates a SFTP specific data storer instance.
        
        @param identifier: Logical identifier of a file system item.
        @type identifier: C{unicode}
        
        @return: TSM specific data storer instance.
        @rtype: L{SftpDataAdapter<datafinder.persistence.adapters.sftp.adapter.SftpDataAdapter>}
        """
        
        persistenceId = self._idMapper.determinePeristenceIdentifier(identifier)
        return SftpDataAdapter(
            identifier, persistenceId, self._connectionPool, self, self._idMapper)
    
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
