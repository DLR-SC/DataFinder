#
# Created: 19.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: adapter.py 3898 2009-04-01 16:39:50Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements adapter for accessing the file system.
"""


from datetime import datetime
import mimetypes
import os
    
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata import constants, value_mapping
from datafinder.persistence.metadata.metadatastorer import NullMetadataStorer


__version__ = "$LastChangedRevision: 3898 $"


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
