#
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
Factory implementation for the standard file system implementation.
"""


from datafinder.persistence.adapters.filesystem.configuration import Configuration
from datafinder.persistence.adapters.filesystem.data.adapter import DataFileSystemAdapter
from datafinder.persistence.adapters.filesystem.metadata.adapter import MetadataFileSystemAdapter
from datafinder.persistence.adapters.filesystem.util import ItemIdentifierMapper, connectWindowsShare
from datafinder.persistence.common.base_factory import BaseFileSystem
from datafinder.persistence.error import PersistenceError


__version__ = "$Revision-Id:$" 


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
        @see: L{FileSystem.isValidIdentifier<datafinder.persistence.factory.FileSystem.metadataIdentifierPattern>}
        @note: This implementation always returns C{True}, C{None}.
        """
        
        return True, None
    
    def isValidMetadataIdentifier(self, name):
        """ 
        @see: L{FileSystem.metadataIdentifier<datafinder.persistence.factory.FileSystem.metadataIdentifierPattern>}
        @note: This implementation always returns C{True}, C{None}.
        """
        
        return True, None
