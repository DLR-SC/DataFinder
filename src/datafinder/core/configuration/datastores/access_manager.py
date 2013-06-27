# $Filename$$
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
Centrally manages file systems required to access external data stores.
"""


import logging

from datafinder.core.error import AuthenticationError
from datafinder.persistence.common import configuration
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.factory import FileSystem


__version__ = "$Revision-Id$" 


_logger = logging.getLogger()


class DataStoreAccessManager(object):
    """ Centrally manages file systems required to access external data stores. """
    
    def __init__(self):
        self._datastoreFileSystemMap = dict()
    
    def getFileSystem(self, datastore):
        """ Provides a file system for the given data store configuration.
        File system instances are created once and cached for later access.
        
        @param datastore: The configuration of the data store.
        @type datastore: L{<DefaultDataStore>datafinder.core.configuration.datastores.datastore.DefaultDataStore}
        
        @return: The file system to access data of the data store.
        @rtype: L{<FileSystem>datafinder.persistence.factory.FileSystem}
        """
        
        return self._findFileSystemEntry(datastore)[0]
        
    def _findFileSystemEntry(self, datastore):
        if not datastore in self._datastoreFileSystemMap:
            self._createFileSystemEntry(datastore)
        return self._datastoreFileSystemMap[datastore] 
        
    def _createFileSystemEntry(self, datastore):
        try:
            fileSystem = self._createFileSystem(datastore)
        except PersistenceError:
            _logger.debug("Unsupported data store interface.", exc_info=True)
            self._datastoreFileSystemMap[datastore] = None, False
        else:
            isAccessible = fileSystem.isAccessible
            self._datastoreFileSystemMap[datastore] = fileSystem, isAccessible
        
    @staticmethod
    def _createFileSystem(datastore):
        baseConfiguration = configuration.BaseConfiguration(datastore.dataLocationUri, **datastore.parameters)
        return FileSystem(baseConfiguration)
       
    def isAccessible(self, datastore):
        """ Indicates whether the file system of the given data store
        can be accessed or not. The method only checks the accessibility once 
        and returns the cached result in succeeding calls.
        
        @param datastore: The configuration of the data store.
        @type datastore: L{<DefaultDataStore>datafinder.core.configuration.datastores.datastore.DefaultDataStore}
        
        @return: Flag indicating the accessibility.
        @rtype: C{bool}
        """
        
        return self._findFileSystemEntry(datastore)[1]
    
    def checkAccessibility(self, datastore):
        """ Explicitly triggers an accessibility check of the file system 
        if it is not already accessible. If authentication credentials 
        are missing, the raised error provides a callback function which 
        sets the new credentials and checks the accessibility again.
        
        @param datastore: The configuration of the data store.
        @type datastore: L{<DefaultDataStore>datafinder.core.configuration.datastores.datastore.DefaultDataStore}
        
        @raise AuthenticationError: Indicates missing/wrong authentication information. 
            The error instance provides a callback to update the credentials.
            @see: L{<AuthenticationError>datafinder.core.error.AuthenticationError}
        """
        
        fileSystem, isAccessible = self._findFileSystemEntry(datastore)
        if not isAccessible and not fileSystem is None:
            self._checkAccessibility(datastore, fileSystem)
            
    def _checkAccessibility(self, datastore, fileSystem):
        isAccessible = fileSystem.isAccessible 
        if isAccessible:
            self._datastoreFileSystemMap[datastore] = fileSystem, isAccessible
        else:
            callback = self._createCredentialCallback(datastore, fileSystem)
            raise AuthenticationError("Authentication credentials are missing!", datastore, callback)
    
    def _createCredentialCallback(self, datastore, fileSystem):
        """ Creates a callback function which allows specification of credentials. """
        
        def _setCredentialCallback(credentials):
            try:
                fileSystem.updateCredentials(credentials)
            except PersistenceError:
                _logger.debug("Credential update is invalid.", exc_info=True)
            isAccessible = fileSystem.isAccessible
            self._datastoreFileSystemMap[datastore] = fileSystem, isAccessible
            return isAccessible
        return _setCredentialCallback
    
    def release(self):
        """ Explicitly triggers the deallocation of resources acquired by the file systems. """
        
        for fileSystem, _ in self._datastoreFileSystemMap.values():
            fileSystem.release() 
