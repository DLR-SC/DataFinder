# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are
#
#met:
#
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



""" Handler for the generated data store stuff. """


import codecs
from copy import deepcopy
from StringIO import StringIO
from xml.parsers.expat import ExpatError

from datafinder.core.configuration.gen import datastores
from datafinder.core.configuration.datastores import constants
from datafinder.core.configuration.datastores import datastore
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.factory import createFileStorer


__version__ = "$Revision-Id:$" 


_typeDataStoreClassMap = {constants.DEFAULT_STORE: datastore.DefaultDataStore,
                          constants.FILE_STORE: datastore.FileDataStore,
                          constants.FTP_STORE: datastore.FtpDataStore,
                          constants.GRIDFTP_STORE: datastore.GridFtpDataStore,
                          constants.OFFLINE_STORE: datastore.OfflineDataStore,
                          constants.TSM_CONNECTOR_STORE: datastore.TsmDataStore,
                          constants.WEBDAV_STORE: datastore.WebdavDataStore,
                          constants.S3_STORE: datastore.S3DataStore,
                          constants.SUBVERSION_STORE: datastore.SubversionDataStore}

  
_DEFAULT_ENCODING = "UTF-8"
datastores.ExternalEncoding = _DEFAULT_ENCODING


class DataStoreHandler(object):
    """ Allows access to the defined data model. """
    
    _NEW_BASE_DATASTORE_NAME = "Data Store"
    _streamWriterClass = codecs.getwriter(_DEFAULT_ENCODING)
    
    def __init__(self, fileStorer):
        """ 
        Constructor.
        
        @param fileStorer: Handles retrieval of the data store configuration file.
        @type fileStorer: L{FileStorer<datafinder.persistence.factory.FileStorer>}
        """
        
        self._fileStorer = fileStorer
        self._datastores = dict()
        
    def create(self, dataUri=None):
        """ 
        Creates the data store configuration. 
        
        @param dataUri: URI pointing to the data location.
        @type dataUri: C{unicode}
        
        @raise ConfigurationError: Indicating problems on creation.
        """
        
        try:
            self._fileStorer.createResource()
            self._datastores.clear()
            self.addDataStore(self.createDataStore(url=dataUri, isDefault=True))
            self.store()
        except PersistenceError, error:
            raise ConfigurationError("Cannot create data store configuration.\nReason: '%s'" % error.message)
        
    def load(self):
        """ Loads the data store configuration. """
        
        try:
            if self._fileStorer.exists():
                stream = self._fileStorer.readData()
            else:
                raise ConfigurationError("The data store configuration does not exist.")
        except PersistenceError, error:
            raise ConfigurationError("Cannot access the data store configuration.\nReason: '%s'" % error.message)
        else:
            try:
                persistedDataStores = datastores.parseString(unicode(stream.read(), _DEFAULT_ENCODING))
            except (ValueError, ExpatError, UnicodeDecodeError), error:
                raise ConfigurationError("Cannot load data store configuration. Reason:'%s'" % error.message)
            else:
                self._loadPersistenceState(persistedDataStores)
            finally:
                stream.close()

    def _loadPersistenceState(self, persistedDataStores):
        """ Loads the persisted state. """
        
        self._datastores.clear()
        for persistedDataStore in persistedDataStores.stores:
            if not persistedDataStore.name is None and not persistedDataStore.storeType is None:
                self._datastores[persistedDataStore.name] = _typeDataStoreClassMap[persistedDataStore.storeType]\
                                                                (persistedStore=persistedDataStore)
                    
    def store(self):
        """ Stores the data store configuration. """
        
        persistedDataStores = self._createPersistedDatastores()
        stream = self._streamWriterClass(StringIO())
        persistedDataStores.export(stream, 0)
        stream.seek(0)
        try:
            self._fileStorer.writeData(stream)
        except PersistenceError, error:
            raise ConfigurationError("Cannot store the data store configuration\nReason: '%s'" % error.message)
        
    def _createPersistedDatastores(self):
        """ Transforms internal state to the persistence format. """
        
        persistedDataStores = list()
        for dataStore in self._datastores.values():
            persistedDataStores.append(dataStore.toPersistenceRepresentation())
        return datastores.datastores(persistedDataStores)

    def exportDataStores(self, localFilePath):
        """
        Exports the data store configuration to the local file path.
        
        @param localFilePath: Path to file on the local file system.
        @type localFilePath: C{unicode}
        """
        
        persistedDataStores = self._createPersistedDatastores()
        stream = self._streamWriterClass(StringIO())
        persistedDataStores.export(stream, 0)
        stream.seek(0)
        try:
            localFileStorer = createFileStorer("file:///" + localFilePath)
            localFileStorer.writeData(stream)
        except PersistenceError, error:
            raise ConfigurationError("Cannot export data model. Reason: '%s'" % error.message)
    
    def importDataStores(self, localFilePath):
        """
        Imports the data store configuration from a local file.
        
        @param localFilePath: Path to file on the local file system.
        @type localFilePath: C{unicode}
        """
        
        try:
            localFileStorer = createFileStorer("file:///" + localFilePath)
            binaryStream = localFileStorer.readData()
        except PersistenceError, error:
            raise ConfigurationError("Cannot import data store configuration.\nReason: '%s'" % error.message)
        else:
            try:
                persistedDataStores = datastores.parseString(binaryStream.read())
            except ExpatError, error:
                raise ConfigurationError("Cannot import data model. Reason: '%s'" % error.message)
            else:
                self._loadPersistenceState(persistedDataStores)

    def createDataStore(self, name=None, storeType=None, iconName="dataStore", url=None, isDefault=False, owner=None):
        """ 
        Creates a data store configuration for the given type.
    
        @param name: Identifier of the data store configuration.
        @type name: C{unicode}
        @param storeType: Type of the data store configuration.
        @type storeType: C{unicode}
        """
        
        dataStoreName = self._determineUniqueDataStoreName(name)
        if storeType is None:
            dataStore = _typeDataStoreClassMap[constants.DEFAULT_STORE](dataStoreName, constants.DEFAULT_STORE, 
                                                                        iconName, url, isDefault, owner)
        else:
            if storeType in _typeDataStoreClassMap:
                dataStore = _typeDataStoreClassMap[storeType](dataStoreName, storeType, iconName, url, isDefault, owner)
            else:
                raise ConfigurationError("The data store type '%s' is not supported." % storeType)   
        return dataStore

    def _determineUniqueDataStoreName(self, name):
        """ Finds a unique name for a new data store. """

        if name is None:
            dataStoreName = self._NEW_BASE_DATASTORE_NAME
        else:
            dataStoreName = name
        if dataStoreName in self._datastores:
            counter = 0
            tmpName = dataStoreName
            while tmpName in self._datastores:
                counter = counter + 1
                tmpName = dataStoreName + (" (%i)" % counter)
            dataStoreName = tmpName
        return dataStoreName

    def setDataStores(self, dataStores):
        """
        Sets the data store configurations.
        
        @param datastores: List of data store configurations.
        @type datastores: C{list} of C{DataStore}
        """
        
        self._datastores.clear()
        for dataStore in dataStores:
            self.addDataStore(dataStore)
    
    def addDataStore(self, dataStore):
        """
        Adds an data store.
        
        @param dataStore: Data store configuration to add.
        @type dataStore: C{DataStore}
        """

        self._datastores[dataStore.name] = deepcopy(dataStore)
    
    def removeDataStore(self, name):
        """
        Removes the data store with the given name.
        
        @param name: Name to identify the corresponding data store configuration.
        @type name: C{unicode}
        """
        
        if name in self._datastores:
            del self._datastores[name]
            
    def getDataStore(self, name):
        """ 
        Returns the data store configuration for the given name.
        
        @param name: Name that identifies the data store.
        @type name: C{unicode}
        
        @return: Data store that corresponds to the name or C{None}.
        @rtype: C{DataStore}
        """
        
        result = None
        if name in self._datastores:
            result = deepcopy(self._datastores[name])
        return result
            
    def hasDataStore(self, name):
        """ 
        Returns the data store configuration for the given name.
        
        @param name: Name that identifies the data store.
        @type name: C{unicode}
        
        @return: Flag indicating existence of the data store associated with the name.
        @rtype: C{bool}
        """
        
        return name in self._datastores
            
    @property
    def datastores(self):
        """ Getter for the data stores encapsulated by the handler. """
        
        result = list()
        for dataStore in self._datastores.values():
            result.append(deepcopy(dataStore))
        return result

    @property
    def archiveDatastores(self):
        """ Retrieves all archive data stores. """
        
        return self._getDataStoreByCategory(constants.ARCHIVE_STORE_CATEGORY)
    
    @property
    def onlineDatastores(self):
        """ Retrieves all online data stores. """
        
        return self._getDataStoreByCategory(constants.ONLINE_STORE_CATEGORY)
    
    @property
    def offlineDatastores(self):
        """ Retrieves all off-line data stores. """
        
        return self._getDataStoreByCategory(constants.OFFLINE_STORE_CATEGORY)
    
    @property
    def externalDatastores(self):
        """ Retrieves all data store which use an external file system. """
        
        return self._getDataStoreByCategory(constants.EXTERNAL_STORE_CATEGORY)
    
    def _getDataStoreByCategory(self, allowedStoreTypes):
        """ Retrieves all archive data stores. """
        
        result = list()
        for dataStore in self._datastores.values():
            if dataStore.storeType in allowedStoreTypes \
               and not getattr(dataStore, "isMigrated", False):
                result.append(deepcopy(dataStore))
        return result

    @property
    def defaultDatastores(self):
        """ Getter for the list of default data stores. """
        
        defaultDataStores = list()
        for dataStore in self._datastores.values():
            if dataStore.isDefault and not getattr(dataStore, "isMigrated", False):
                defaultDataStores.append(deepcopy(dataStore))
        return defaultDataStores
        
    @property
    def defaultDataUris(self):
        """ Retrieves the data URIs where corresponding data is stored. """
        
        primaryDataUris = list()
        secondaryDataUris = list()
        for dataStore in self._datastores.values():
            if not dataStore.url is None:
                if dataStore.isDefault:
                    if not dataStore.url in primaryDataUris:
                        primaryDataUris.append(dataStore.url)
                else:
                    if not dataStore.url in primaryDataUris:
                        secondaryDataUris.append(dataStore.url)
        for uri in secondaryDataUris:
            if not uri in primaryDataUris:
                primaryDataUris.append(uri)
        return primaryDataUris
