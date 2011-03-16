# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
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
Implements the Subversion factory.
"""


from datafinder.persistence.common.base_factory import BaseFileSystem
from datafinder.persistence.common.connection.manager import ConnectionPoolManager
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.adapters.svn import constants
from datafinder.persistence.adapters.svn.configuration import Configuration
from datafinder.persistence.adapters.svn.connection_pool import SubversionConnectionPool
from datafinder.persistence.adapters.svn.data.adapter import DataSubversionAdapter
from datafinder.persistence.adapters.svn.metadata.adapter import MetadataSubversionAdapter


__version__ = "$Revision-Id$" 


class FileSystem(BaseFileSystem):
    """ 
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
        self._connectionPool = self._getConnectionPool()
        
    def _getConnectionPool(self):
        """ Creates / retrieves a usable connection pool for the given configuration. """
        
        connectionPool = self._connectionManager.get(self._configuration.baseUrl)
        if connectionPool is None:
            connectionPool = SubversionConnectionPool(self._configuration)
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
        Factory Method providing a SVN-specific data storer. 
        
        @return: SVN-specific implementation of the data interface.
        @rtype: L{DataSubversionAdapter<datafinder.persistence.adapters.svn.
        data.adapter.DataSubversionAdapter>
        """
        
        return DataSubversionAdapter(identifier, self._connectionPool)    
    
    def createMetadataStorer(self, identifier):
        """ 
        Factory Method providing a SVN-specific meta data storer. 
        
        @return: SVN-specific implementation of the meta data interface.
        @rtype: L{MetadataSubversionAdapter<datafinder.persistence.adapters.svn.
        metadata.adapter.MetadataSubversionAdapter>
        """

        return MetadataSubversionAdapter(identifier, self._connectionPool)
    
    def release(self):
        """ Releases the acquired connection pool. """
        
        self._connectionManager.remove(self._configuration.baseUrl)
        
    @property
    def hasCustomMetadataSupport(self):
        """ 
        This is the SVN-specific implementation.
        @note: Always returns C{True} because custom meta data support is a built-in SVN feature.
        @see: L{FileSystem.hasCustomMetadataSupport<datafinder.persistence.factory.FileSystem.hasCustomMetadataSupport>}
        """
        
        return True
    
    @property
    def canHandleLocation(self):
        """ Checks whether the location is accessible. """
        
        try:
            connection = self._getConnectionPool().acquire()
        except PersistenceError:
            return False
        else:
            self._getConnectionPool().release(connection)
            return True
