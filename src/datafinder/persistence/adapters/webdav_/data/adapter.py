#
# Created: 28.01.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: adapter.py 4607 2010-04-14 13:27:38Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements adapter for manipulating a WebDAV file system.
"""


import types
        
from webdav.Connection import WebdavError
from webdav.Constants import CODE_NOT_FOUND

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.data.datastorer import NullDataStorer
from datafinder.persistence.adapters.webdav_ import constants, util


__version__ = "$LastChangedRevision: 4607 $"



_PROPERTY_NOT_FOUND_MESSAGE = "Property is missing"


class DataWebdavAdapter(NullDataStorer):
    """ An adapter instance represents an item within the WebDAV file system. """

    def __init__(self, identifier, connectionPool, itemIdMapper, connectionHelper=util, resourceTypeCache=dict()):
        """
        Constructor.
        
        @param identifier: Logical identifier of the resource.
        @type identifier: C{unicode}
        @param connectionPool: Connection pool.
        @type connectionPool: L{Connection<datafinder.persistence.webdav_.connection_pool.WebdavConnectionPool>}
        @param itemIdMapper: Utility object mapping item identifiers. 
        @type itemIdMapper: L{ItemIdentifierMapper<datafinder.persistence.adapters.webdav_.util.ItemIdentifierMapper}
        @param connectionHelper: Utility object/module creating WebDAV library storer instances.
        @type connectionHelper: L{ItemIdentifierMapper<datafinder.persistence.adapters.webdav_.util}
        @param resourceTypeCache: Cache for resource type information. Identifier => isCollection, linkTargetPath
        @type resourceTypeCache: C{dict} keys:C{unicode}, values:C{tuple} of C{bool}, C{unicoe}
        """

        NullDataStorer.__init__(self, identifier)
        self._connectionPool = connectionPool
        self._itemIdMapper = itemIdMapper
        self._persistenceId = self._itemIdMapper.mapIdentifier(identifier)
        self._name = self._itemIdMapper.determineBaseName(identifier)
        self._connectionHelper = connectionHelper
        self._resourceTypeCache = resourceTypeCache

    @property
    def linkTarget(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        return self._determineResourceType()[1]
        
    @property
    def isLink(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        linkTargetPath = self._determineResourceType()[1]
        if not linkTargetPath is None:
            return True
        else:
            return False
        
    @property
    def isLeaf(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        isCollection, linkTargetPath = self._determineResourceType()
        if not linkTargetPath is None:
            return False
        else:
            return not isCollection
        
    @property
    def canAddChildren(self):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        return self.isCollection
    
    def _determineResourceType(self):
        """ Returns resource type and link target path. """
        
        if self.identifier in self._resourceTypeCache:
            isCollection, linkTargetPath = self._resourceTypeCache[self.identifier]
        else:
            connection = self._connectionPool.acquire()
            try:
                resourceStorer = self._connectionHelper.createResourceStorer(self._persistenceId, connection)
                try:
                    isCollection, linkTargetPath = self._connectionHelper.determineResourceType(resourceStorer).values()[0]
                except WebdavError, error:
                    errorMessage = u"Cannot determine resource type of '%s'. Reason: '%s'" % (self.identifier, error.reason)
                    raise PersistenceError(errorMessage)
            finally:
                self._connectionPool.release(connection)
        return isCollection, linkTargetPath
    
    @property
    def isCollection(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        isCollection, linkTargetPath = self._determineResourceType()
        if not linkTargetPath is None:
            return False
        else:
            return isCollection

    def createLink(self, destination):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """

        self.createResource()
        connection = self._connectionPool.acquire()
        try:
            resourceStorer = self._connectionHelper.createResourceStorer(self._persistenceId, connection)
            try:
                resourceStorer.writeProperties({constants.LINK_TARGET_PROPERTY:destination.identifier})
            except WebdavError, error:
                raise PersistenceError("Cannot set property. Reason: '%s'" % error.reason)
        finally:
            self._connectionPool.release(connection)
            
    def createResource(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """

        if len(self._name) == 0:
            raise PersistenceError("Cannot create item with empty resource name.")
        else:
            connection = self._connectionPool.acquire()
            try:
                parentCollection = self._getParentCollectionStorer(connection)
                try:
                    parentCollection.addResource(self._name)
                except WebdavError, error:
                    errorMessage = u"Cannot create resource '%s'. Reason: '%s'" % (self.identifier, error.reason)
                    raise PersistenceError(errorMessage)
            finally:
                self._connectionPool.release(connection)

    def _getParentCollectionStorer(self, connection):
        """ Prepares the parent collection storer. """
        
        parentCollectionPath = self._itemIdMapper.determineParentPath(self.identifier)
        parentPersistenceId = self._itemIdMapper.mapIdentifier(parentCollectionPath)
        return self._connectionHelper.createCollectionStorer(parentPersistenceId, connection)

    def createCollection(self, recursively=False):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """

        if len(self._name) == 0:
            raise PersistenceError("Cannot create item with empty resource name.")
        else:
            if recursively:
                parent = self._getParent()
                if not parent.exists():
                    parent.createCollection(True)
            connection = self._connectionPool.acquire()
            try:
                parentCollection = self._getParentCollectionStorer(connection)
                try:
                    parentCollection.addCollection(self._name)
                except WebdavError, error:
                    errorMessage = u"Cannot create collection '%s'. Reason: '%s'" % (self.identifier, error.reason)
                    raise PersistenceError(errorMessage)
            finally:
                self._connectionPool.release(connection)

    def _getParent(self):
        """ Helper which creates the parent data storer. """
        
        parentId = self._itemIdMapper.determineParentPath(self.identifier)
        return DataWebdavAdapter(parentId, self._connectionPool, self._itemIdMapper, self._connectionHelper, self._resourceTypeCache)

    def getChildren(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """

        connection = self._connectionPool.acquire()
        try:
            result = list()
            resourceStorer = self._connectionHelper.createResourceStorer(self._persistenceId, connection, False)
            try:
                rawResult = self._connectionHelper.determineResourceType(resourceStorer, True)
            except WebdavError, error:
                errorMessage = u"Cannot retrieve children of item '%s'. Reason: '%s'" % (self.identifier, error.reason)
                raise PersistenceError(errorMessage)
            else:
                for path, resourceType in rawResult.iteritems():
                    isCollection, linkTargetPath = resourceType
                    identifier = self._itemIdMapper.mapPersistenceIdentifier(path)
                    self._resourceTypeCache[identifier] = (isCollection, linkTargetPath)
                    if identifier != self.identifier:
                        result.append(identifier)
                return result
        finally:
            self._connectionPool.release(connection)
            
    def writeData(self, dataStream):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            resourceStorer = self._connectionHelper.createResourceStorer(self._persistenceId, connection)
            try:
                if isinstance(dataStream, types.FileType):
                    connection.connect()
                    resourceStorer.uploadFile(dataStream)
                else:
                    content = dataStream.read()
                    resourceStorer.uploadContent(content)
            except WebdavError, error:
                errorMessage = "Unable to write data to '%s'. " % self.identifier + \
                               "Reason: %s" % error.reason
                raise PersistenceError(errorMessage)
            except IOError, error:
                errorMessage = "Cannot read from stream. Reason: '%s'" % error.message
                raise PersistenceError(errorMessage)
        finally:
            dataStream.close()
            self._connectionPool.release(connection)

    def readData(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            resourceStorer = self._connectionHelper.createResourceStorer(self._persistenceId, connection)
            try:
                return resourceStorer.downloadContent()
            except WebdavError, error:
                errorMessage = "Unable to read data from '%s'. " % self.identifier + \
                               "Reason: %s" % error.reason
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
 
    def delete(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            resourceStorer = self._connectionHelper.createResourceStorer(self._persistenceId, connection, False)
            try:
                resourceStorer.delete()
                if self.identifier in self._resourceTypeCache:
                    del self._resourceTypeCache[self.identifier]
            except WebdavError, error:
                errorMessage = "Unable to delete item '%s'. " % self.identifier \
                               + "Reason: %s" % error.reason
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)

    def move(self, destination):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            resourceStorer = self._connectionHelper.createResourceStorer(self._persistenceId, connection, False)
            destinationPersistenceId = self._itemIdMapper.mapIdentifier(destination.identifier)
            try:
                resourceStorer.move(destinationPersistenceId)
                if self.identifier in self._resourceTypeCache:
                    del self._resourceTypeCache[self.identifier]
            except WebdavError, error:
                errorMessage = "Unable to move item '%s' to '%s'. " % (self.identifier, destination.identifier) \
                               + "Reason: %s" % error.reason
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
            
    def copy(self, destination):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        connection = self._connectionPool.acquire()
        try:
            resourceStorer = self._connectionHelper.createResourceStorer(self._persistenceId, connection, False)
            destinationPersistenceId = self._itemIdMapper.mapIdentifier(destination.identifier)
            try:
                resourceStorer.copy(destinationPersistenceId)
            except WebdavError, error:
                errorMessage = "Unable to copy item '%s' to '%s'. " % (self.identifier, destination.identifier) \
                               + "Reason: %s" % error.reason
                raise PersistenceError(errorMessage)
        finally:
            self._connectionPool.release(connection)
        
    def exists(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        exists = True
        try:
            connection = self._connectionPool.acquire()
            try:
                resourceStorer = self._connectionHelper.createResourceStorer(self._persistenceId, connection)
                return not self._connectionHelper.determineResourceType(resourceStorer) is None
            except WebdavError, error:
                if error.code == CODE_NOT_FOUND:
                    exists = False
                else:
                    raise PersistenceError("Cannot determine item existence. Reason: '%s'" % error.reason)
        finally:
            self._connectionPool.release(connection)
        return exists
