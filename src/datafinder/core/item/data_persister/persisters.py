# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#
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
This is the default data persister which is intended to store data and
access data on the same file system.
"""


import atexit
import logging
import os
import random
from tempfile import mkstemp
import time

from hashlib import sha1

from datafinder.core.error import ItemError
from datafinder.core.configuration.properties.constants import CONTENT_IDENTIFIER_ID, \
                                                               ARCHIVE_ROOT_COLLECTION_ID, \
                                                               ARCHIVE_PART_COUNT_ID, \
                                                               ARCHIVE_PART_INDEX_ID
from datafinder.core.item.property import Property

from datafinder.persistence.common.configuration import BaseConfiguration
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.factory import FileSystem


__version__ = "$Revision-Id:$" 


_log = logging.getLogger(__name__)
_BLOCK_SIZE = 30000

def _generateUniqueIdentifier(uri):
    """ Generates an unique name from the given URI. """
    
    firstTime = time.time()
    time.sleep(random.random())
    secondTime = time.time()
    return sha1(uri + str(firstTime + secondTime)).hexdigest()


class NullDataPersister(object):
    """ 
    Null-pattern-like implementation of a data persister.
    Objects of this class are associated with items that own no binary data, e.g. simple collections.
    """
    
    def __init__(self, dataState, fileStorer=None):
        """
        Constructor.
        
        @param dataState: Data state constant associated with the item.
        @type dataState: C{unicode} 
        @param fileStorer: The file storer is used to access the data.
        @type fileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        """
        
        self._dataState = dataState
        self._fileStorer = fileStorer
    
    def create(self):
        """ Performs additional actions on item creation. """
        
        pass
    
    def delete(self):
        """ Performs additional actions on item deletion. """
        
        pass
        
    def copy(self, item):
        """
        Performs additional actions on item copying.
        
        @param item: The already created target item of the copy.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        pass
    
    def move(self, item):
        """
        Performs additional actions on item moving.
        
        @param item: The new item after moving.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        """
        
        pass
    
    def retrieveData(self, index=0):
        """
        Retrieves the data associated with the referenced item.
        
        @param index: Optional parameter identifying the "block" where the required is contained. Default: C{0}
        @type index: C{int\
        
        @return: File-like object usable for reading data.
        @rtype: C{object} implementing the file protocol.
        """

        pass
    
    def storeData(self, fileObj):
        """
        Writes the data to the associated file resource.
        
        @param fileObj: File-like object used for reading data.
        @type fileObj: C{object} implementing the file protocol.
        """
        
        pass

    @property
    def fileStorer(self):
        """ Returns the encapsulated file storer. """
        
        return self._fileStorer

    @property
    def state(self):
        """ Returns the data state constant. """
        
        return self._dataState


class DefaultDataPersister(NullDataPersister):
    """ 
    This is the default data persister which is intended to 
    store data and access data on the same file system.
    """
    
    def __init__(self, dataState, fileStorer):
        """ Constructor. """
        
        NullDataPersister.__init__(self, dataState, fileStorer)

    def retrieveData(self, index=0):
        """
        Data is directly retrieved from the associated file storer object.
        """
        
        _log.debug(index)
        return self._fileStorer.readData()
    
    def storeData(self, fileObj):
        """
        Data is directly written to the associated file storer object.
        """
        
        self._fileStorer.writeData(fileObj)


class FlatDataPersister(DefaultDataPersister):
    """ Implements the data behavior allowing access to external storage resource. """
    
    def __init__(self, dataState, baseFileStorer, item, propertyRegistry, testFileSystemAccessiblityCallback):
        """ 
        Constructor. 

        @param dataState: Data state constant associated with the item.
        @type dataState: C{unicode}
        @param item: Item data persister is associated with.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        @param baseFileStorer: The file storer representing the root collection of the separated storage system.
        @type baseFileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        @param propertyRegistry: Reference to the property definition registry.
        @type propertyRegistry: L{PropertyDefinitionRegistry<datafinder.core.configuration.
        properties.registry.PropertyDefinitionRegistry>} 
        @param testFileSystemAccessiblityCallback: Callback allowing the of accessibility of the file system.
        @type testFileSystemAccessiblityCallback: C{Callable}
        """
        
        DefaultDataPersister.__init__(self, dataState, None)
        self._baseFileStorer = baseFileStorer
        self._item = item
        self._propertyRegistry = propertyRegistry
        self._testFileSystemAccessiblityCallback = testFileSystemAccessiblityCallback
        
        if CONTENT_IDENTIFIER_ID in item.properties:
            uniqueName = item.properties[CONTENT_IDENTIFIER_ID].value
            self._fileStorer = self._baseFileStorer.getChild(uniqueName)
        
    def _prepareAction(self):
        """ Helper method performing common preparation steps. """
        
        self._testFileSystemAccessiblityCallback(self._baseFileStorer.fileSystem)
        if self._fileStorer is None:
            uniqueName = _generateUniqueIdentifier(self._item.uri)
            self._fileStorer = self._baseFileStorer.getChild(uniqueName)
        
    def create(self):
        """ 
        Initially creates the referenced file resource on the separated storage system. 
        Additionally, sets the content identifier property in the item properties.
        This is required to identify the resource on the separated storage system. 
        """

        self._prepareAction()
        if self._fileStorer.exists():
            raise ItemError("The unique identifier '%s' generated for item '%s' does already exist." \
                            % (self._fileStorer.name, self._item.path))
        else:
            self._fileStorer.createResource()
            propertyDefinition = self._propertyRegistry.getPropertyDefinition(CONTENT_IDENTIFIER_ID)
            self._item.updateProperties([Property(propertyDefinition, self._fileStorer.name)])
            if not CONTENT_IDENTIFIER_ID in self._item.properties:
                raise ItemError("Unable to set the unique identifier property " \
                                + "to '%s' for item '%s'." % (self._fileStorer.name, self._item.path))
            
    def delete(self):
        """ Additionally performs deletion of the file resource on separated storage system. """
        
        self._prepareAction()
        self._fileStorer.delete()
        
    def copy(self, item):
        """ 
        Duplicates resource with the help of the data persister of the newly created target item.
        Updates the properties of the target item accordingly.
        """

        self._prepareAction()
        self._testFileSystemAccessiblityCallback(self._baseFileStorer.fileSystem)
        uniqueName = _generateUniqueIdentifier(item.uri)
        targetFileStorer = self._baseFileStorer.getChild(uniqueName)
        self._fileStorer.copy(targetFileStorer)
        
        propertyDefinition = self._propertyRegistry.getPropertyDefinition(CONTENT_IDENTIFIER_ID)
        item.updateProperties([Property(propertyDefinition, uniqueName)])
        item._dataPersister = None
        if not CONTENT_IDENTIFIER_ID in item.properties:
            raise ItemError("Unable to set the unique identifier property " \
                            + "to '%s' for item '%s'." % (uniqueName, item.path))

    def retrieveData(self, index=0):
        """ Additionally ensure creation of the file storer instance. """
        
        _log.debug(index)
        self._prepareAction()
        return DefaultDataPersister.retrieveData(self)
        
    def storeData(self, fileObj):
        """ Additionally ensure creation of the file storer instance. """
        
        self._prepareAction()
        return DefaultDataPersister.storeData(self, fileObj)
        

class HierarchicalDataPersister(DefaultDataPersister):
    """ Implements the data behavior allowing access to external storage resource. """
    
    def __init__(self, dataState, fileStorer, testFileSystemAccessiblityCallback):
        """
        Constructor. 
        
        @param dataState: Data state constant associated with the item.
        @type dataState: C{unicode}
        @param fileStorer: The file storer representing the associated file resource.
        @type fileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        @param testFileSystemAccessiblityCallback: Callback allowing the of accessibility of the file system.
        @type testFileSystemAccessiblityCallback: C{Callable}
        """
        
        DefaultDataPersister.__init__(self, dataState, fileStorer)
        self._testFileSystemAccessiblityCallback = testFileSystemAccessiblityCallback

    def create(self):
        """ Creates the file resource on separated storage system under the path of the item. """
        
        self._testFileSystemAccessiblityCallback(self.fileStorer.fileSystem)
        if not self._fileStorer.exists():
            self._createParentCollection(self._fileStorer.parent)
            self._fileStorer.createResource()
        else:
            errorMessage = "The data persister '%s' does already exist." % (self._fileStorer.identifier)
            raise ItemError(errorMessage)
        
    def delete(self):
        """ Deletes on the file resource on separated storage system and cleans up created directories. """

        self._testFileSystemAccessiblityCallback(self.fileStorer.fileSystem)
        self._fileStorer.delete()
        self._cleanupCollections()
        
    def _cleanupCollections(self):
        """ Removes empty collections. """
        
        parent = self._fileStorer.parent
        while parent.name != "" and len(parent.getChildren()) == 0:
            parent.delete()
            parent = parent.parent
    
    def copy(self, item):
        """ Duplicates the file resource under the path of the given target item. """

        self._testFileSystemAccessiblityCallback(self.fileStorer.fileSystem)
        destFileStorer = item.dataPersister.fileStorer
        self._createParentCollection(destFileStorer.parent)
        self._fileStorer.copy(destFileStorer)
    
    def move(self, item):
        """ Move the file resource to the path of the target item. """

        self._testFileSystemAccessiblityCallback(self.fileStorer.fileSystem)
        destFileStorer = item.dataPersister.fileStorer
        self._createParentCollection(destFileStorer.parent)
        self._fileStorer.move(destFileStorer)
        self._cleanupCollections()
        
    @staticmethod
    def _createParentCollection(fileStorer):
        """ Helper function for creation of parent collection/directory structure. """
    
        if not fileStorer.exists():
            fileStorer.createCollection(True)


class ArchiveDataPersister(DefaultDataPersister):
    """
    This class implements a data persister that can retrieve and store data of archive root.
    """
    
    def __init__(self, dataState, item, baseDataPersister):
        """
        Constructor.
        
        @param dataState: Data state constant associated with the item.
        @type dataState: C{unicode} 
        @param item: The item this persister is associated with.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        @param baseDataPersister: The data persister used to store data.
        @type baseDataPersister: L{DefaultDataPersister<datafinder.core.item.data_persister.persisters.DefaultDataPersister>}
        """
        
        super(ArchiveDataPersister, self).__init__(dataState, None)
        self._item = item
        self._baseDataPersister = baseDataPersister
        self._count = int(item.properties[ARCHIVE_PART_COUNT_ID].value)
    
    @property
    def fileStorer(self):
        """ Returns the file storer object of the associated data persister. """
        
        return self._baseDataPersister.fileStorer
    
    def create(self):
        """ @see: L{create<datafinder.core.item.data_persister.persisters.NullDataPersister.create>} """
        
        self._baseDataPersister.create()
            
    def delete(self):
        """ @see: L{delete<datafinder.core.item.data_persister.persisters.NullDataPersister.delete>} """
        
        if self._count > 0:
            for index in range(1, self._count):
                self._determineFileStorer(index).delete()
            self._baseDataPersister.delete()
    
    def _determineFileStorer(self, index=0):
        """ Returns the file storer associated with given index. """
        
        fileStorer = self._baseDataPersister.fileStorer
        name = fileStorer.name
        if index > 0:
            name += "_" + str(index)
        return fileStorer.parent.getChild(name)
        
    def copy(self, item):
        """ @see: L{copy<datafinder.core.item.data_persister.persisters.NullDataPersister.copy>} """
        
        self._baseDataPersister.copy(item)
        destBaseName = item.dataPersister.fileStorer.name
        destBaseFileStorer = item.dataPersister.fileStorer.parent
        for index in range(1, self._count):
            fileStorer = self._determineFileStorer(index)
            fileStorer.copy(destBaseFileStorer.getChild(destBaseName + "_" + str(index)))
                
    def move(self, item):
        """ @see: L{move<datafinder.core.item.data_persister.persisters.NullDataPersister.move>} """
        
        if item.dataUri != self._item.dataUri:
            if not item.dataPersister.fileStorer.parent.exists():
                item.dataPersister.fileStorer.parent.createCollection(True)
            destBaseName = item.dataPersister.fileStorer.name
            destBaseFileStorer = item.dataPersister.fileStorer.parent
            for index in range(1, self._count):
                fileStorer = self._determineFileStorer(index)
                fileStorer.move(destBaseFileStorer.getChild(destBaseName + "_" + str(index)))
            self._baseDataPersister.move(item)
            
    def retrieveData(self, index=0):
        """ @see: L{retrieveData<datafinder.core.item.data_persister.persisters.NullDataPersister.retrieveData>} """
        
        _log.debug(index)
        return self._determineFileStorer(index).readData()
        
    def storeData(self, fileObj):
        """ @see: L{storeData<datafinder.core.item.data_persister.persisters.NullDataPersister.storeData>} """

        fileStorer = self._determineFileStorer(self._count)
        property_ = self._item.properties[ARCHIVE_PART_COUNT_ID]
        property_.value = property_.value + 1
        self._item._ignoreChecks = True
        try:
            self._item.updateProperties([property_])
            self._count += 1
            try:
                if not fileStorer.exists():
                    fileStorer.createResource()
                fileStorer.writeData(fileObj)
            except PersistenceError, error:
                self._count -= 1
                property_.value = property_.value - 1
                self._item.updateProperties([property_])
                raise error
        finally:
            self._item._ignoreChecks = False
 

class ArchiveMemberDataPersister(NullDataPersister):
    """
    This class implements a data persister that can retrieve and store data of archive members.
    """
    
    def __init__(self, dataState, item, rootItem, propertyRegistry):
        """
        Constructor.
        
        @param dataState: Data state constant associated with the item.
        @type dataState: C{unicode} 
        @param item: The item this persister is associated with.
        @type item: L{ItemBase<datafinder.core.item.base.ItemBase>}
        @param rootItem: The item that represents the stored archive (i.e. the ZIP file).
        @type rootItem: L{ItemBase<datafinder.core.item.base.ItemBase}
        @param propertyRegistry: Reference to the property definition registry.
        @type propertyRegistry: L{PropertyDefinitionRegistry<datafinder.core.configuration.
        properties.registry.PropertyDefinitionRegistry>} 
        """
        
        super(ArchiveMemberDataPersister, self).__init__(dataState, None)
        self._item = item
        self._propertyRegistry = propertyRegistry
        self._rootItem = rootItem
        self._fileSystem = None
        self._index = int(item.properties[ARCHIVE_PART_INDEX_ID].value)
        
    def _ensureReadableSystem(self):
        """
        Make sure, self._archiveFileSystem contains a valid readable file system. If
        none is present, the corresponding ZIP file will be downloaded.
        """
        
        if self._fileSystem is None:
            key = self._rootItem.path + str(self._index)
            if key in _temporaryFileMap:
                self._fileSystem = _temporaryFileMap[key][1]
            else:
                fd, path = mkstemp()
                fileHandle = os.fdopen(fd, "w+b")
                inStream = self._rootItem.dataPersister.retrieveData(self._index)
                try:
                    block = inStream.read(_BLOCK_SIZE)
                    while len(block) > 0:
                        fileHandle.write(block)
                        block = inStream.read(_BLOCK_SIZE)
                        while len(block) > 0:
                            fileHandle.write(block)
                            block = inStream.read(_BLOCK_SIZE)
                    fileHandle.close()
                except (OSError, IOError), error:
                    reason = os.strerror(error.errno or 0)
                    raise ItemError("Cannot retrieve archive.\nReason: '%s'" % reason)
                else:
                    config = BaseConfiguration('arch:' + path)
                    _log.debug("Downloaded %s to %s." % (self._rootItem.path, path))
                    self._fileSystem = FileSystem(config)
                    _temporaryFileMap[key] = (path, self._fileSystem)

    def copy(self, item):
        """ @see: L{copy<datafinder.core.item.data_persister.persisters.NullDataPersister.copy>} """
        
        self.move(item)
        
    def move(self, item):
        """ @see: L{move<datafinder.core.item.data_persister.persisters.NullDataPersister.move>} """
        
        pathWithoutRootArchive = self._item.path[len(self._rootItem.path):]
        newArchiveRootPath = item.path[:item.path.rfind(pathWithoutRootArchive)]
        propDef = self._propertyRegistry.getPropertyDefinition(ARCHIVE_ROOT_COLLECTION_ID)
        archiveRootProperty = Property(propDef, newArchiveRootPath)
        item.updateProperties([archiveRootProperty])
        
    def retrieveData(self, index=0):
        """ @see: L{retrieveData<datafinder.core.item.data_persister.persisters.NullDataPersister.retrieveData>} """
        
        _log.debug(index)
        self._ensureReadableSystem()
        return self.fileStorer.readData()
    
    @property
    def fileStorer(self):
        """ Returns the encapsulated file storer. """
        
        if self._fileSystem is None:
            self._ensureReadableSystem()
        if self._fileStorer is None:
            innerPath = self._item.path[len(self._rootItem.path):]
            self._fileStorer = self._fileSystem.createFileStorer(innerPath)
        return self._fileStorer


_temporaryFileMap = dict()

    
def _cleanupTemporaryFiles():
    """ Cleans up the temporary created files on application exit. """

    for filePath, fileSystem in _temporaryFileMap.values():
        try:
            fileSystem.release()
            os.remove(filePath)
        except (OSError, PersistenceError):
            _log.error("Cannot clean up temporary file '%s'" % filePath)


atexit.register(_cleanupTemporaryFiles)
