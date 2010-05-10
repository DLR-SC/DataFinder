#
# Created: 18.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: adapter.py 4621 2010-04-19 16:00:42Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements a file system specific data adapter
"""


import os
import shutil
    
from datafinder.persistence.adapters.filesystem import util
from datafinder.persistence.data.datastorer import NullDataStorer
from datafinder.persistence.error import PersistenceError

                                                
__version__ = "$LastChangedRevision: 4621 $"


_BLOCK_SIZE = 30000


class DataFileSystemAdapter(NullDataStorer):
    """ Implements data storer interface for a standard file system. """

    def __init__(self, identifier, itemIdMapper):
        """ 
        Constructor.
        
        @param identifier: Identifier of the item.
        @type identifier: C{unicode}
        @param itemIdMapper: Utility object allowing item identifier mapping.
        @type itemIdMapper: L{ItemIdentifierMapper<datafinder.persistence.adapters.filesystem.util.ItemIdentifierMapper>}
        """
        
        NullDataStorer.__init__(self, identifier)
        self._itemIdMapper = itemIdMapper
        self._persistenceId = self._itemIdMapper.mapIdentifier(identifier)

    @property
    def linkTarget(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        link = util.ShortCut(self._persistenceId)
        if link.isLink():
            persistenceId = link.resolve()
            return self._itemIdMapper.mapPersistenceIdentifier(persistenceId)

    @property
    def isLink(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        return util.createShortcut(self._persistenceId).isLink()

    @property
    def isCollection(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        return os.path.isdir(self._persistenceId)

    @property
    def isLeaf(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        return os.path.isfile(self._persistenceId)
    
    @property
    def canAddChildren(self):
        """
        @see L{NullDataStorer<datafinder.persistence.data.datastorer.NullDataStorer>}
        """
        
        canAddChildren = False
        if self.isCollection and not util.isWindowsRootPath(self._persistenceId):
            canAddChildren = True
        return canAddChildren 

    def createCollection(self, recursively=False):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        try:
            if recursively:
                os.makedirs(self._persistenceId)
            else:
                os.mkdir(self._persistenceId)
        except OSError, error:
            reason = os.strerror(error.errno)
            errorMessage = "Cannot create collection '%s'. Reason: '%s'" % (self.identifier, reason)
            raise PersistenceError(errorMessage)

    def createResource(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        try:
            fd = open(self._persistenceId, "wb")
            fd.close()
        except IOError, error:
            reason = os.strerror(error.errno)
            errorMessage = "Cannot create resource '%s'. Reason: '%s'" % (self.identifier, reason)
            raise PersistenceError(errorMessage)

    def createLink(self, source):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        link = util.createShortcut(self._persistenceId)
        link.create(self._itemIdMapper.mapIdentifier(source.identifier))

    def getChildren(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        mappedIds = list()
        rawResult = list()
        if self.isCollection:
            try:
                rawResult = util.listDirectory(self._persistenceId)
            except OSError, error:
                reason = os.strerror(error.errno)
                errorMessage = "Cannot retrieve children of '%s'. Reason: '%s'." % (self.identifier, reason)
                raise PersistenceError(errorMessage)
        for persistenceId in rawResult:
            mappedIds.append(self._itemIdMapper.mapPersistenceIdentifier(persistenceId))
        return mappedIds

    def exists(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        return os.path.exists(self._persistenceId)

    def delete(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        try:
            if self.isCollection:
                shutil.rmtree(self._persistenceId)
            else:
                os.remove(self._persistenceId)
        except OSError, error:
            reason = os.strerror(error.errno)
            errorMessage = "Cannot delete item '%s'. Reason: '%s'." % (self.identifier, reason)
            raise PersistenceError(errorMessage)
        except shutil.Error, error:
            errorMessage = "Cannot delete item '%s'. Reason: '%s'." % (self.identifier, reason)
            raise PersistenceError(errorMessage)

    def copy(self, destination):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        try:
            targetPersistenceId = self._itemIdMapper.mapIdentifier(destination.identifier)
            if self.isCollection:
                shutil.copytree(self._persistenceId, targetPersistenceId)
            else:
                shutil.copy(self._persistenceId, targetPersistenceId)
        except (IOError, OSError, EnvironmentError), error:
            reason = os.strerror(error.errno or 0)
            errorMessage = "Cannot copy item '%s' to item '%s'. Reason: '%s'." % (self.identifier, destination.identifier, reason)
            raise PersistenceError(errorMessage)
        
    def move(self, destination):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        try:
            os.rename(self._persistenceId, self._itemIdMapper.mapIdentifier(destination.identifier))
        except OSError, error:
            reason = os.strerror(error.errno)
            errorMessage = "Cannot move item '%s' to item '%s'. Reason: '%s'." % (self.identifier, destination.identifier, reason)
            raise PersistenceError(errorMessage)
 
    def readData(self):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        try:
            return open(self._persistenceId, "rb")
        except IOError, error:
            reason = os.strerror(error.errno)
            errorMessage = "Cannot read item data '%s'. Reason: '%s'." % (self.identifier, reason)
            raise PersistenceError(errorMessage)

    def writeData(self, dataStream):
        """ @see: L{NullDataStorer<datafinder.persistence.metadata.metadatastorer.NullDataStorer>} """
        
        try:
            fd = open(self._persistenceId, "wb")
            try:
                block = dataStream.read(_BLOCK_SIZE)
                while len(block) > 0:
                    fd.write(block)
                    block = dataStream.read(_BLOCK_SIZE)
            finally:
                fd.close()
        except IOError, error:
            reason = os.strerror(error.errno)
            errorMessage = "Cannot read item data '%s'. Reason: '%s'." % (self.identifier, reason)
            raise PersistenceError(errorMessage)
        finally:
            dataStream.close()
