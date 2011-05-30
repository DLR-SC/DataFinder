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
import logging
import mimetypes

from datafinder.persistence.adapters.svn.constants import JSON_PROPERTY_NAME
from datafinder.persistence.adapters.svn.error import SubversionError
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata import constants as const
from datafinder.persistence.metadata.value_mapping import custom_format
from datafinder.persistence.metadata.value_mapping import json_format
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
        """
        
        NullMetadataStorer.__init__(self, identifier)
        self.__connectionPool = connectionPool

    def retrieve(self, propertyIds=None):
        """ @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}"""

        connection = self.__connectionPool.acquire()
        try:
            properties = self._retrieveCustomProperties(connection)
            for key, value in properties.iteritems():
                properties[key] = json_format.MetadataValue(value)
            systemProperties = self._retrieveSystemProperties(connection)
            properties.update(systemProperties)
            return self._filterResult(propertyIds, properties)
        finally:
            self.__connectionPool.release(connection)

    @staticmethod
    def _filterResult(propertyIds, properties):
        if not propertyIds is None and len(propertyIds) > 0:
            filteredProps = dict()
            for propertyId in propertyIds:
                if propertyId in properties:
                    filteredProps[propertyId] = properties[propertyId]
        else:
            filteredProps = properties
        return filteredProps

    def _retrieveCustomProperties(self, connection):
        customProperties = dict()
        try:
            jsonString = connection.getProperty(self.identifier, JSON_PROPERTY_NAME)
            if not jsonString is None:
                customProperties = json_format.convertFromPersistenceFormat(jsonString)
        except SubversionError, error:
            raise PersistenceError(str(error))
        return customProperties
        
    def _retrieveSystemProperties(self, connection):
        try:
            rawSystemProps = connection.info(self.identifier)
        except SubversionError, error:
            errorMessage = "Problem during meta data retrieval. " \
                           + "Reason: '%s'" % str(error) 
            raise PersistenceError(errorMessage)
        else:
            systemProps = dict()
            systemProps[const.CREATION_DATETIME] = \
                custom_format.MetadataValue(rawSystemProps["creationDate"] or "", datetime.datetime)
            systemProps[const.MODIFICATION_DATETIME] = \
                custom_format.MetadataValue(rawSystemProps["lastChangedDate"] or "", datetime.datetime)
            systemProps[const.SIZE] = custom_format.MetadataValue(rawSystemProps["size"] or "")
            systemProps[const.OWNER] = custom_format.MetadataValue(rawSystemProps["owner"] or "")
            systemProps[const.MIME_TYPE] = custom_format.MetadataValue(self._guessMimeType() or "")
            return systemProps

    def _guessMimeType(self):
        return mimetypes.guess_type(self.identifier, False)[0]
    
    def update(self, properties):
        """ @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}"""

        connection = self.__connectionPool.acquire()
        try:
            customProperties = self._retrieveCustomProperties(connection)
            customProperties.update(properties)
            newJsonString = json_format.convertToPersistenceFormat(customProperties)
            try:
                connection.setProperty(self.identifier, JSON_PROPERTY_NAME, newJsonString)
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
            customProperties = self._retrieveCustomProperties(connection)
            for propertyId in propertyIds:
                if propertyId in customProperties:
                    del customProperties[propertyId]
            newJsonString = json_format.convertToPersistenceFormat(customProperties)
            try:
                connection.setProperty(self.identifier, JSON_PROPERTY_NAME, newJsonString)
            except SubversionError, error:
                errorMessage = "Cannot delete properties of item '%s'. " % self.identifier \
                               + "Reason: '%s'" % error 
                raise PersistenceError(errorMessage)
        finally:
            self.__connectionPool.release(connection)
