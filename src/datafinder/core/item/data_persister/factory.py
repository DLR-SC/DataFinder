#pylint: disable=W0142
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
Factory for creation of data persister.
"""


from datafinder.core.configuration.datastores.constants import DEFAULT_STORE, OFFLINE_STORE, STORAGE_REALISATION_MODE_ENUM
from datafinder.core.error import CoreError, AuthenticationError
from datafinder.core.configuration.properties import constants as property_constants
from datafinder.core.item.data_persister import constants
from datafinder.core.item.data_persister import persisters
from datafinder.persistence.common.configuration import BaseConfiguration
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.factory import FileSystem


__version__ = "$Revision-Id:$" 


class DataPersisterFactory(object):
    """ Factory creating corresponding data persister. """
    
    def __init__(self, configuration):
        """
        Constructor.
        
        @param configuration: The repository configuration.
        @type configuration: L{RepositoryConfiguration<datafinder.core.configuration.configuration.RepositoryCOnfiguration>}
        """
        
        self._configuration = configuration
        self._configurationFileSystemsMap = dict()
        self._fileSystemAccessible = list()
        
    def createDataPersister(self, item):
        """ Creates the suitable data persister and attaches it to the item. """

        datastore = self._determineDatastore(item)
        dataState = self._determineDataState(item, datastore)
        
        if dataState == constants.ITEM_STATE_ARCHIVED_MEMBER:
            rootItemPath = item.properties[property_constants.ARCHIVE_ROOT_COLLECTION_ID].value
            rootItem = item.itemFactory.create(rootItemPath)
            dataPersister = persisters.ArchiveMemberDataPersister(dataState, item, rootItem, self._configuration)
        elif dataState in [constants.ITEM_STATE_NULL, constants.ITEM_STATE_INACCESSIBLE, 
                           constants.ITEM_STATE_UNSUPPORTED_STORAGE_INTERFACE]:
            dataPersister = persisters.NullDataPersister(dataState)
        elif datastore is None or datastore.storeType == DEFAULT_STORE:
            dataPersister = persisters.DefaultDataPersister(dataState, item.fileStorer)
        else:
            try:
                fileSystem = self._getFileSystem(datastore)
            except PersistenceError:
                dataPersister = persisters.NullDataPersister(constants.ITEM_STATE_UNSUPPORTED_STORAGE_INTERFACE)
            else:
                if datastore.storageRealisation == STORAGE_REALISATION_MODE_ENUM.FLAT:
                    baseFileStorer = fileSystem.createFileStorer("/")
                    dataPersister = persisters.FlatDataPersister(dataState, baseFileStorer, item, 
                                                                 self._configuration, self._testFileSystemAccessiblityCallback)
                else:
                    fileStorer = self._createHierachicalFileStorer(datastore, fileSystem, item.path)
                    dataPersister = persisters.HierarchicalDataPersister(dataState, fileStorer, self._testFileSystemAccessiblityCallback)
                if property_constants.ARCHIVE_PART_COUNT_ID in item.properties:
                    dataPersister = persisters.ArchiveDataPersister(dataState, item, dataPersister)
        return dataPersister

    def _determineDatastore(self, item):
        """ Determines the data store configuration. """
        
        try:
            datastoreName = item.properties[property_constants.DATASTORE_NAME_ID].value
            datastore = self._configuration.getDataStore(datastoreName)
        except KeyError:
            datastore = None
        return datastore
    
    def _determineDataState(self, item, datastore):
        """ Determines the data state constant. """
        
        if datastore is None and property_constants.DATASTORE_NAME_ID in item.properties:
            dataState = constants.ITEM_STATE_UNSUPPORTED_STORAGE_INTERFACE
        elif datastore is None: # items without data store AND data store information
            if item.isLink:
                dataState = constants.ITEM_STATE_NULL
            elif item.isCollection:
                dataState = constants.ITEM_STATE_NULL
                if property_constants.ARCHIVE_ROOT_COLLECTION_ID in item.properties:
                    dataState = constants.ITEM_STATE_ARCHIVED_MEMBER
            else:
                dataState = constants.ITEM_STATE_ACCESSIBLE
        else: # items with valid data store
            dataState = self.__determineDataState(datastore, item)
        return dataState
    
    @staticmethod
    def __determineDataState(datastore, item):
        """ Determines data state of items with valid data store. """
        
        dataState = constants.ITEM_STATE_ACCESSIBLE
        if property_constants.ARCHIVE_ROOT_COLLECTION_ID in item.properties:
            dataState = constants.ITEM_STATE_ARCHIVED_MEMBER
            rootItem = item.itemFactory.create(item.properties[property_constants.ARCHIVE_ROOT_COLLECTION_ID].value)
            if rootItem.state == constants.ITEM_STATE_MIGRATED:
                dataState = constants.ITEM_STATE_MIGRATED
        elif datastore.storeType == OFFLINE_STORE:
            dataState = constants.ITEM_STATE_INACCESSIBLE
        elif datastore.isMigrated:
            dataState = constants.ITEM_STATE_MIGRATED
        elif property_constants.ARCHIVE_RETENTION_EXCEEDED_DATETIME_ID in item.properties:
            try:
                if datastore.readOnly:
                    dataState = constants.ITEM_STATE_ARCHIVED_READONLY
                else:
                    dataState = constants.ITEM_STATE_ARCHIVED
            except AttributeError:
                dataState = constants.ITEM_STATE_ARCHIVED
        return dataState
                
    def _getFileSystem(self, datastore):
        """ Returns the corresponding file storer factory. """
        
        if not datastore in self._configurationFileSystemsMap:
            baseConfiguration = BaseConfiguration(datastore.dataLocationUri, **datastore.parameters)
            self._configurationFileSystemsMap[datastore] = FileSystem(baseConfiguration)
            self._fileSystemAccessible.append(False)
        return self._configurationFileSystemsMap[datastore]
    
    def _testFileSystemAccessiblityCallback(self, fileSystem):
        """ Tests the file system accessibility. """
        
        try:
            index = self._configurationFileSystemsMap.values().index(fileSystem)
            datastore = self._configurationFileSystemsMap.keys()[index]
            fileSystemAccessible = self._fileSystemAccessible[index]
        except (IndexError, ValueError):
            raise CoreError("Internally managed file systems are inconsistent.")
        else:
            if not fileSystemAccessible:
                if not fileSystem.isAccessible:
                    raise AuthenticationError("Problem accessing storage resource '%s' occurred." % datastore.name,
                                              datastore, self._createCredentialCallback(fileSystem))
                else:
                    self._fileSystemAccessible[index] = True

    @staticmethod
    def _createCredentialCallback(fileSystem):
        """ Creates a callback function which allows specification of credentials. """
        
        def _setCredentialCallback(credentials):
            """ Callback for setting storage-specific credentials. """
            
            try:
                fileSystem.updateCredentials(credentials)
            except PersistenceError:
                raise CoreError("Authentication information update is invalid")
            
    @staticmethod
    def _createHierachicalFileStorer(datastore, fileStorerFactory, path):
        """ Creates for the given item path the specific file storer object. """
        
        effectivePath = path
        try:
            if path.startswith(datastore.removePathPrefix):
                effectivePath = path[len(datastore.removePathPrefix):]
                if not effectivePath.startswith("/"):
                    effectivePath = "/" + effectivePath
                if effectivePath.endswith("/"):
                    effectivePath = effectivePath[-1]
        except AttributeError:
            effectivePath = path
        return fileStorerFactory.createFileStorer(effectivePath)
