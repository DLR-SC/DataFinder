# pylint: disable=W0142
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
This module implements how the meta data is persisted on the WebDAV server.
"""


from webdav.Connection import WebdavError
from webdav import Constants
from webdav.NameCheck import WrongNameError 

from datafinder.persistence.adapters.webdav_.metadata import identifier_mapping
from datafinder.persistence.adapters.webdav_.metadata.search_restriction_mapping import mapSearchRestriction
from datafinder.persistence.adapters.webdav_ import util
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata import constants, value_mapping
from datafinder.persistence.metadata.metadatastorer import NullMetadataStorer


__version__ = "$Revision-Id:$" 

 
class MetadataWebdavAdapter(NullMetadataStorer):
    """ This class implements property retrieval, storage and deletion using the WebDAV protocol. """
    
    def __init__(self, identifier, connectionPool, itemIdMapper, metadataIdMapper=identifier_mapping, connectionHelper=util,
                 hasMetadataSearchSupport=True):
        """
        Constructor.
        
        @param identifier: Logical identifier of the resource.
        @type identifier: C{unicode}
        @param connectionPool: Connection pool.
        @type connectionPool: L{Connection<datafinder.persistence.webdav_.connection_pool.WebdavConnectionPool>}
        @param itemIdMapper: Utility object mapping item identifiers. 
        @type itemIdMapper: L{ItemIdentifierMapper<datafinder.persistence.adapters.webdav_.util.ItemIdentifierMapper}
        @param metadataIdMapper: Utility object/module mapping meta data item identifiers.
        @type metadataIdMapper: L{ItemIdentifierMapper<datafinder.persistence.adapters.webdav_.metadata.identifier_mapping}
        @param connectionHelper: Utility object/module creating WebDAV library storer instances.
        @type connectionHelper: L{ItemIdentifierMapper<datafinder.persistence.adapters.webdav_.util}
        """

        NullMetadataStorer.__init__(self, identifier)
        self.__connectionPool = connectionPool
        self.__itemIdMapper = itemIdMapper
        self.__metadataIdMapper = metadataIdMapper
        self._persistenceId = self.__itemIdMapper.mapIdentifier(identifier)
        self.__connectionHelper = connectionHelper
        self.__hasMetadataSearchSupport = hasMetadataSearchSupport

    def retrieve(self, propertyIds=None):
        """ @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}"""

        connection = self.__connectionPool.acquire()
        try:
            if propertyIds is None:
                persistenceProperties = self._retrieveAllProperties(connection)
                properties = {constants.CREATION_DATETIME: value_mapping.MetadataValue(""), 
                              constants.MODIFICATION_DATETIME: value_mapping.MetadataValue(""),
                              constants.SIZE: value_mapping.MetadataValue("0"), 
                              constants.MIME_TYPE: value_mapping.MetadataValue(""), 
                              constants.OWNER: value_mapping.MetadataValue("")}
            else:
                persistenceIds = [self.__metadataIdMapper.mapMetadataId(propertyId) for propertyId in propertyIds]
                persistenceProperties = self._retrieveProperties(connection, persistenceIds)
                properties = dict()
            
            for persistenceId, value in persistenceProperties.iteritems():
                logicalId = self.__metadataIdMapper.mapPersistenceMetadataId(persistenceId)
                if not logicalId is None:
                    representationValue = self._getMetadataValue(persistenceId, value)
                    properties[logicalId] = representationValue
            return properties
        finally:
            self.__connectionPool.release(connection)
    
    def _retrieveAllProperties(self, connection):
        """ Retrieves all properties. """
        
        webdavStorer = self.__connectionHelper.createResourceStorer(self._persistenceId, connection)
        try:
            return webdavStorer.readAllProperties()
        except WebdavError, error:
            errorMessage = "Problem during meta data retrieval." \
                           + "Reason: '%s'" % error.reason 
            raise PersistenceError(errorMessage)
        
    def _retrieveProperties(self, connection, propertyIds):
        """ Retrieves the specified set of properties. """
        
        result = dict()
        if len(propertyIds) > 0:
            webdavStorer = self.__connectionHelper.createResourceStorer(self._persistenceId, connection)
            try:
                result = webdavStorer.readProperties(*propertyIds)
            except WebdavError, error:
                errorMessage = "Problem during meta data retrieval." \
                               + "Reason: '%s'" % error.reason 
                raise PersistenceError(errorMessage)
        return result
    
    @staticmethod
    def _getMetadataValue(persistenceId, peristedValueAsXml):
        """ 
        Adapts the retrieved XML representation of the WebDAV
        library and returns an according value representation.
    
        @param persistenceId: Identifier on the persistence layer (namespace, name).
        @type persistenceId: C{tuple} of C{string}, C{string}
        
        @return: Value representation that can be converted to different Python types.
        @rtype: C{value_mapping.MetadataValue}
        """
        
        persistedValueAsString = ""
        if (Constants.NS_DAV, Constants.PROP_OWNER) == persistenceId:
            if len(peristedValueAsXml.children) > 0:
                persistedValueAsString = peristedValueAsXml.children[0].textof()
        else:  
            persistedValueAsString = peristedValueAsXml.textof()
        return value_mapping.MetadataValue(persistedValueAsString)

    def update(self, properties):
        """ @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}"""

        connection = self.__connectionPool.acquire()
        try:
            persistencePropertyValueMapping = dict()
            for propertyId, value in properties.iteritems():
                persistenceId = self.__metadataIdMapper.mapMetadataId(propertyId)
                persistenceValue = value_mapping.getPersistenceRepresentation(value)
                persistencePropertyValueMapping[persistenceId] = persistenceValue
            webdavStorer = self.__connectionHelper.createResourceStorer(self._persistenceId, connection)
            try:
                webdavStorer.writeProperties(persistencePropertyValueMapping)
            except WebdavError, error:
                errorMessage = "Cannot update properties of item '%s'" % self.identifier \
                               + "Reason: '%s'" % error.reason 
                raise PersistenceError(errorMessage)
            except WrongNameError:
                raise PersistenceError("Cannot update properties because invalid characters " \
                                       + "are contained within an identifier.")
        finally:
            self.__connectionPool.release(connection)

    def delete(self, propertyIds):
        """ @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}"""
        
        connection = self.__connectionPool.acquire()
        try:
            persistenceIds = [self.__metadataIdMapper.mapMetadataId(propertyId) for propertyId in propertyIds]
            webdavStorer = self.__connectionHelper.createResourceStorer(self._persistenceId, connection)
            try:
                webdavStorer.deleteProperties(None, *persistenceIds)
            except WebdavError, error:
                errorMessage = "Cannot delete properties of item '%s'" % self.identifier \
                               + "Reason: '%s'" % error.reason 
                raise PersistenceError(errorMessage)
        finally:
            self.__connectionPool.release(connection)

    def search(self, restrictions):
        """ @see: L{NullMetadataStorer<datafinder.persistence.metadata.metadatastorer.NullMetadataStorer>}"""
        
        result = list()
        if self.__hasMetadataSearchSupport:
            connection = self.__connectionPool.acquire()
            try:
                try:
                    restrictions = mapSearchRestriction(restrictions)
                except AssertionError:
                    restrictions = list()
                collectionStorer = self.__connectionHelper.createCollectionStorer(self._persistenceId, connection)
                try:
                    rawResult = collectionStorer.search(restrictions, [Constants.PROP_DISPLAY_NAME])
                except WebdavError, error:
                    errorMessage = "Problem during meta data search." \
                                   + "Reason: '%s'" % error.reason 
                    raise PersistenceError(errorMessage)
                else:
                    for persistenceId in rawResult.keys():
                        result.append(self.__itemIdMapper.mapPersistenceIdentifier(persistenceId))
            finally:
                self.__connectionPool.release(connection)
        return result
