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
Implements adapter for accessing the file system.
"""


from datetime import datetime
import mimetypes
import os
    
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata import constants, value_mapping
from datafinder.persistence.metadata.metadatastorer import NullMetadataStorer


__version__ = "$Revision-Id:$" 


class MetadataFileSystemAdapter(NullMetadataStorer):
    """ Implements meta data storer interface for a standard file system. """
    
    def __init__(self, identifier, itemIdMapper):
        """ 
        Constructor.
        
        @param identifier: Identifier of the item.
        @type identifier: C{unicode}
        @param itemIdMapper: Utility object allowing item identifier mapping.
        @type itemIdMapper: L{ItemIdentifierMapper<datafinder.persistence.adapters.filesystem.util.ItemIdentifierMapper>}
        """
        
        NullMetadataStorer.__init__(self, identifier)
        self.__itemIdMapper = itemIdMapper
        self.__persistenceId = self.__itemIdMapper.mapIdentifier(identifier)
        
    def retrieve(self, propertyIds=None):
        """ @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}"""
        
        try:
            rawResult = os.stat(self.__persistenceId)
        except OSError, error:
            reason = os.strerror(error.errno)
            errorMessage = "Cannot retrieve properties of collection '%s'. Reason: '%s'" % (self.identifier, reason)
            raise PersistenceError(errorMessage)
        else:
            mappedResult = self._mapRawResult(rawResult)
            return self._filterResult(propertyIds, mappedResult)

    def _mapRawResult(self, rawResult):
        """ Maps the os module specific result to interface format. """
        
        mappedResult = dict()
        mappedResult[constants.CREATION_DATETIME] = value_mapping.MetadataValue(str(rawResult.st_ctime), datetime)
        mappedResult[constants.MODIFICATION_DATETIME] = value_mapping.MetadataValue(str(rawResult.st_mtime), datetime)
        mappedResult[constants.SIZE] = value_mapping.MetadataValue(str(rawResult.st_size))
        mappedResult[constants.OWNER] = value_mapping.MetadataValue("")

        mimeType = mimetypes.guess_type(self.__persistenceId, False)
        if mimeType[0] is None:
            mappedResult[constants.MIME_TYPE] = value_mapping.MetadataValue("")
        else:
            mappedResult[constants.MIME_TYPE] = value_mapping.MetadataValue(mimeType[0])
        return mappedResult
        
    @staticmethod
    def _filterResult(selectedPropertyIds, mappedResult):
        """ Filters the result so it contains only the specified properties. """
        
        if not selectedPropertyIds is None and len(selectedPropertyIds) > 0:
            result = dict()
            for propertyId in selectedPropertyIds:
                if propertyId in mappedResult:
                    result[propertyId] = mappedResult[propertyId]
            return result
        else:
            return mappedResult

    def update(self, properties):
        """ 
        Unsupported delegating to default implementation.
        @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}
        """
        
        return NullMetadataStorer.update(self, properties)

    def delete(self, propertyIds):
        """ 
        Unsupported delegating to default implementation.
        @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}
        """
        
        return NullMetadataStorer.delete(self, propertyIds)

    def search(self, restrictions):
        """ 
        Unsupported delegating to default implementation.
        @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}
        """
        
        return NullMetadataStorer.search(self, restrictions)
