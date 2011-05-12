# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#
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
This module implements how the meta data is persisted on the SVN server.
"""


import datetime
import json
import logging
import mimetypes
import os

from datafinder.persistence.adapters.svn.constants import XPS_JSON_PROPERTY, SVN_MIME_TYPE
from datafinder.persistence.adapters.svn.error import SubversionError
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata import constants, value_mapping
from datafinder.persistence.metadata.metadatastorer import NullMetadataStorer


__version__ = "$Revision-Id$" 


_log = logging.getLogger()


class MetadataSubversionAdapter(NullMetadataStorer):
    """ Implements meta data storer interface for subversion. """
    
    def __init__(self, identifier, connectionPool):
        """
        Constructor.
        
        @param identifier: Logical identifier of the resource.
        @type identifier: C{unicode}
        @param connectionPool: Connection pool.
        @type connectionPool: L{Connection<datafinder.persistence.svn.connection_pool.SVNConnectionPool>}
        @param modelIdentifier: Logical identifier of the model.
        @type modelIdentifier: C{unicode}
        """
        
        NullMetadataStorer.__init__(self, identifier)
        self.__connectionPool = connectionPool

    def retrieve(self, propertyIds=None):
        """ @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}"""

        connection = self.__connectionPool.acquire()
        try:
            rawResult = dict()
            try:
                persistenceJsonProperties = self._retrieveProperties(connection)
                if not persistenceJsonProperties is None:
                    rawResult = json.loads(persistenceJsonProperties)
            except SubversionError, error:
                raise PersistenceError(repr(error))
            mappedResult = self._mapRawResult(connection, rawResult)
            return self._filterResult(propertyIds, mappedResult)
        finally:
            self.__connectionPool.release(connection)

    def _retrieveProperties(self, connection):
        """ Retrieves all properties. """

        return connection.getProperty(self.identifier, XPS_JSON_PROPERTY)
        
    def _mapRawResult(self, connection, rawResult):
        """ Maps the SVN specific result to interface format. """
        
        try:
            infoDict = connection.info(self.identifier)
        except SubversionError, error:
            errorMessage = "Problem during meta data retrieval. " \
                           + "Reason: '%s'" % error 
            raise PersistenceError(errorMessage)
        except OSError, error:
            reason = os.strerror(error.errno)
            errorMessage = "Cannot retrieve properties of collection '%s'. Reason: '%s'" % (self.identifier, reason)
            raise PersistenceError(errorMessage)  
        mappedResult = dict()
        mappedResult[constants.CREATION_DATETIME] = value_mapping.MetadataValue(infoDict["creationDate"], \
                                                                                 expectedType=datetime.datetime)
        try:
            mappedResult[constants.MODIFICATION_DATETIME] = value_mapping.MetadataValue(infoDict["lastChangedDate"], \
                                                                                        expectedType=datetime.datetime)
            mappedResult[constants.SIZE] = value_mapping.MetadataValue(infoDict["size"])
            mappedResult[constants.OWNER] = value_mapping.MetadataValue(infoDict["owner"])
        except KeyError, error:
            errorMessage = "Cannot get properties of item '%s'. " % self.identifier \
                           + "Reason: '%s'" % error 
            raise PersistenceError(errorMessage)
        try:
            mimeType = connection.getProperty(self.identifier, SVN_MIME_TYPE)
            mappedResult[constants.MIME_TYPE] = value_mapping.MetadataValue(mimeType)
        except SubversionError:
            _log.debug("No subversion property for mimetype is set! Trying to determine mimetype by persitenceId.")
            mimeType = mimetypes.guess_type(self.identifier, False)
            if mimeType[0] is None:
                mappedResult[constants.MIME_TYPE] = value_mapping.MetadataValue("")
            else:
                mappedResult[constants.MIME_TYPE] = value_mapping.MetadataValue(mimeType[0])
        for key, value in rawResult.iteritems():
            mappedResult[key] = value_mapping.MetadataValue(value)
        return mappedResult
    
    @staticmethod
    def _filterResult(selectedPropertyIds, mappedResult):
        """ Filters the result so it contains only the specified properties. """
        
        if not selectedPropertyIds is None and len(selectedPropertyIds) >= 0:
            result = dict()
            for propertyId in selectedPropertyIds:
                if propertyId in mappedResult:
                    result[propertyId] = mappedResult[propertyId]
            return result
        else:
            return mappedResult

    def update(self, properties):
        """ @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}"""

        connection = self.__connectionPool.acquire()
        try:
            try:
                try:
                    persistenceProperties = dict()
                    persistenceJsonProperties = self._retrieveProperties(connection)
                    if not persistenceJsonProperties is None:
                        persistenceProperties = json.loads(persistenceJsonProperties)
                    persistenceProperties.update(properties)
                except SubversionError, error:
                    _log.debug("No subversion property is set!")
                jsonProperties = value_mapping.getPersistenceRepresentation(persistenceProperties)
                connection.setProperty(self.identifier, XPS_JSON_PROPERTY, jsonProperties)
            except SubversionError, error:
                errorMessage = "Cannot update properties of item '%s'. " % self.identifier \
                               + "Reason: '%s'" % error 
                raise PersistenceError(errorMessage)
        finally:
            self.__connectionPool.release(connection)
    
    def delete(self, propertyIds):
        """ @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}"""
        
        connection = self.__connectionPool.acquire()
        try:
            try:
                persistenceJsonProperties = self._retrieveProperties(connection)
                persistenceProperties = json.loads(persistenceJsonProperties)
                for propertyId in propertyIds:
                    if propertyId in persistenceProperties:
                        del persistenceProperties[propertyId]
                persistenceJsonProperties = json.dumps(persistenceProperties)
                connection.setProperty(self.identifier, XPS_JSON_PROPERTY, persistenceJsonProperties)
            except SubversionError, error:
                errorMessage = "Cannot delete properties of item '%s'. " % self.identifier \
                               + "Reason: '%s'" % error 
                raise PersistenceError(errorMessage)
            except KeyError, error:
                errorMessage = "Cannot delete properties of item '%s'. " % self.identifier \
                               + "Reason: '%s'" % error 
                raise PersistenceError(errorMessage)
        finally:
            self.__connectionPool.release(connection)
