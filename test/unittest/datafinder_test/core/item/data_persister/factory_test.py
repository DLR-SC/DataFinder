#
# Created: 18.05.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: factory_test.py 4596 2010-04-10 21:45:52Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests for the data persister factory.
"""


import unittest

from datafinder.core.configuration.datastores.constants import DEFAULT_STORE, OFFLINE_STORE, STORAGE_REALISATION_MODE_ENUM
from datafinder.core.configuration.properties.constants import DATASTORE_NAME_ID, ARCHIVE_ROOT_COLLECTION_ID, \
                                                               ARCHIVE_RETENTION_EXCEEDED_DATETIME_ID,\
    ARCHIVE_PART_INDEX_ID, ARCHIVE_PART_COUNT_ID
from datafinder.core.item.data_persister import constants, factory, persisters
from datafinder.core.error import AuthenticationError, CoreError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4596 $"


class _FileSystemMock(object):
    """ Helper class for mocking file storer creation. """

    def __init__(self):
        """ Constructor. """
        
        self.isAccessible = False
        
    def createFileStorer(self, identifier):
        """ Mocks factory method. """

        fileStorerMock = SimpleMock(identifier=identifier, fileSystem=self,
                                    parent=SimpleMock(list(), name=""))
        fileStorerMock.value = fileStorerMock
        return fileStorerMock
    
    
class DataPersisterFactoryTestCase(unittest.TestCase):
    """ Tests the data persister factory. """
    
    def setUp(self):
        """ Creates the object under test. """
        
        self._configurationMock = SimpleMock()
        self._itemMock = SimpleMock(uri="uri", path="/root/data/inst/MyProject",
                                    properties = {DATASTORE_NAME_ID: SimpleMock(value=None)},
                                    itemFactory=SimpleMock(SimpleMock(state="")))
        self._dataStoreMock = SimpleMock(name="test", storeType=DEFAULT_STORE, isMigrated=False, 
                                         dataLocationUri="", parameters=dict())
        self._fileSystemMock = _FileSystemMock()
        self._factory = factory.DataPersisterFactory(self._configurationMock)
        
    def testCreateDataPersiterWithoutDataStore(self):
        """ Tests the data persister creation of items which own no data store property. """
        
        self._itemMock.isCollection = False
        self._itemMock.isLink = True
        self._itemMock.properties = dict()
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_NULL)
        self.assertTrue(isinstance(dataPersister, persisters.NullDataPersister))

        self._itemMock.isCollection = True
        self._itemMock.isLink = False
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_NULL)
        self.assertTrue(isinstance(dataPersister, persisters.NullDataPersister))

        self._itemMock.isCollection = False
        self._itemMock.isLink = False
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_ACCESSIBLE)
        self.assertTrue(isinstance(dataPersister, persisters.DefaultDataPersister))
        
    def testCreateDataPersiterWithCommonDataStores(self):
        """ Tests the data persister creation for items which own a data store property. """

        self._factory._determineDatastore = SimpleMock(self._dataStoreMock)
        self._factory._getFileSystem = SimpleMock(self._fileSystemMock)
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_ACCESSIBLE)
        self.assertTrue(isinstance(dataPersister, persisters.DefaultDataPersister))

        self._dataStoreMock.storeType = OFFLINE_STORE
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_INACCESSIBLE)
        self.assertTrue(isinstance(dataPersister, persisters.NullDataPersister))
        
        self._dataStoreMock.storeType = DEFAULT_STORE
        self._dataStoreMock.isMigrated = True
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_MIGRATED)
        self.assertTrue(isinstance(dataPersister, persisters.NullDataPersister))
    
    def testCreateDataPersiterWithArchivalDataStore(self):
        """ Tests the creation with archival data stores. """

        self._factory._determineDatastore = SimpleMock(self._dataStoreMock)
        self._factory._getFileSystem = SimpleMock(self._fileSystemMock)
        self._itemMock.fileStorer = SimpleMock()
        self._itemMock.properties[ARCHIVE_ROOT_COLLECTION_ID] = SimpleMock(value=None)
        self._itemMock.properties[ARCHIVE_PART_INDEX_ID] = SimpleMock(value=0)
        self._dataStoreMock.storeType = ""
        self._dataStoreMock.isMigrated = False
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_ARCHIVED_MEMBER)
        self.assertTrue(isinstance(dataPersister, persisters.NullDataPersister))
        
        self._itemMock.properties[ARCHIVE_RETENTION_EXCEEDED_DATETIME_ID] = SimpleMock(value=None)
        self._itemMock.properties[ARCHIVE_PART_COUNT_ID] = SimpleMock(value=0)
        del self._itemMock.properties[ARCHIVE_ROOT_COLLECTION_ID]
        del self._itemMock.properties[ARCHIVE_PART_INDEX_ID]
        self._dataStoreMock.storageRealisation = STORAGE_REALISATION_MODE_ENUM.FLAT
        self._dataStoreMock.readOnly = False
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_ARCHIVED)
        self.assertTrue(isinstance(dataPersister, persisters.ArchiveDataPersister))
        
        self._dataStoreMock.readOnly = True
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_ARCHIVED_READONLY)
        self.assertTrue(isinstance(dataPersister, persisters.ArchiveDataPersister))

    def testCreateDataPersiterWithHierachicalDataStore(self):
        """ Tests the creation with hierarchical data stores. """

        self._factory._determineDatastore = SimpleMock(self._dataStoreMock)
        self._factory._getFileSystem = SimpleMock(self._fileSystemMock)
        self._dataStoreMock.storeType = ""
        self._dataStoreMock.storageRealisation = STORAGE_REALISATION_MODE_ENUM.HIERARCHICAL
        self._dataStoreMock.removePathPrefix = ""
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_ACCESSIBLE)
        self.assertTrue(isinstance(dataPersister, persisters.HierarchicalDataPersister))
        self.assertEquals(dataPersister.fileStorer.identifier, self._itemMock.path)
        
        self._dataStoreMock.removePathPrefix = "/root/data/"
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_ACCESSIBLE)
        self.assertTrue(isinstance(dataPersister, persisters.HierarchicalDataPersister))
        self.assertEquals(dataPersister.fileStorer.identifier, "/inst/MyProject")
        
        self._dataStoreMock.removePathPrefix = "This does not fit."
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_ACCESSIBLE)
        self.assertTrue(isinstance(dataPersister, persisters.HierarchicalDataPersister))
        self.assertEquals(dataPersister.fileStorer.identifier, self._itemMock.path)
  
    def testFileSystemAccessibility(self):
        """ Tests the check accessibility callback. """
        
        self._factory._determineDatastore = SimpleMock(self._dataStoreMock)
        self._factory._getFileSystem = SimpleMock(self._fileSystemMock)
        self._dataStoreMock.storeType = ""
        self._dataStoreMock.storageRealisation = STORAGE_REALISATION_MODE_ENUM.FLAT
        self._dataStoreMock.removePathPrefix = ""
        self._factory._configurationFileSystemsMap = {self._dataStoreMock:self._fileSystemMock}
        self._factory._fileSystemAccessible = [True]
        dataPersister = self._factory.createDataPersister(self._itemMock)
        dataPersister.delete()
        
        self._factory._fileSystemAccessible = [False]
        self._fileSystemMock.isAccessible = True
        dataPersister = self._factory.createDataPersister(self._itemMock)
        dataPersister.delete()
        
        self._factory._fileSystemAccessible = [False]
        self._fileSystemMock.isAccessible = False
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertRaises(AuthenticationError, dataPersister.delete)
        
        self._factory._fileSystemAccessible = list()
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertRaises(CoreError, dataPersister.delete)
        
    def testErrorHandling(self):
        """ Tests the error handling. """
        
        self._itemMock.properties = {DATASTORE_NAME_ID: SimpleMock(value=None)}
        self._factory._determineDatastore = SimpleMock()
        self._factory._getFileSystem = SimpleMock(self._fileSystemMock)
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_UNSUPPORTED_STORAGE_INTERFACE)
        self.assertTrue(isinstance(dataPersister, persisters.NullDataPersister))
        
        self._itemMock.properties = {DATASTORE_NAME_ID: SimpleMock(value=None)}
        self._dataStoreMock.storeType = ""
        self._factory._determineDatastore = SimpleMock(self._dataStoreMock)
        self._factory._getFileSystem = SimpleMock(error=PersistenceError)
        dataPersister = self._factory.createDataPersister(self._itemMock)
        self.assertEquals(dataPersister.state, constants.ITEM_STATE_UNSUPPORTED_STORAGE_INTERFACE)
        self.assertTrue(isinstance(dataPersister, persisters.NullDataPersister))
