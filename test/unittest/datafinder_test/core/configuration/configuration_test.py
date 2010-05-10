#
# Created: 22.05.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: configuration_test.py 4450 2010-02-09 16:30:51Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests the repository configuration.
"""


import unittest

from datafinder.core.configuration import configuration
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4450 $"


class RepositoryConfigurationTest(unittest.TestCase):
    """ Tests the repository configuration. """
    
    def setUp(self):
        """ Creates test setup. """

        self._propertyDefinitionFactoryMock = SimpleMock()
        self._propertyDefinitionRegistryMock = SimpleMock()
        self._iconRegistryMock = SimpleMock()
        self._dataFormatRegistryMock = SimpleMock()
        self._dataModelHandlerMock = SimpleMock()
        self._dataStoreHandlerMock = SimpleMock(defaultDataUris=["http://test.de/path/data1", "http://test.de/path/data2"])
        self._iconHandlerMock = SimpleMock()
        self._scriptHandlerMock = SimpleMock()
        self._configurationCollectionMock = SimpleMock(uri="http://test.de/path/config", fileSystem=SimpleMock(SimpleMock()))
        self._configuration = configuration.RepositoryConfiguration(self._propertyDefinitionFactoryMock, 
                                                                    self._propertyDefinitionRegistryMock,
                                                                    self._iconRegistryMock,
                                                                    self._dataFormatRegistryMock)
        self._configuration.setManagedRepositoryParameters(self._configurationCollectionMock, 
                                                           self._dataModelHandlerMock, 
                                                           self._dataStoreHandlerMock,
                                                           self._iconHandlerMock,
                                                           self._scriptHandlerMock,
                                                           SimpleMock())
        
    def testCreate(self):
        """ Tests the creation of the repository configuration. """
        
        self._configuration.create()
        
        self._configurationCollectionMock.value = True
        self.assertRaises(ConfigurationError, self._configuration.create)
        
        self._configuration.create(overwrite=True)
        
        self._configurationCollectionMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._configuration.create)
        
        self._configurationCollectionMock.error = None
        self._dataModelHandlerMock.error = ConfigurationError("")
        self.assertRaises(ConfigurationError, self._configuration.create)
        
        self._configuration._configurationCollection = None # Test for unmanaged repository
        self._configuration.create()
        
    def testLoad(self):
        """ Tests the configuration loading. """
        
        self._configurationCollectionMock.value = True
        self._configuration.load()
        
        self._configurationCollectionMock.value = False
        self.assertRaises(ConfigurationError, self._configuration.load)
        
        self._configurationCollectionMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._configuration.load)
        
        self._configurationCollectionMock.error = None
        self._dataModelHandlerMock.error = ConfigurationError("")
        self.assertRaises(ConfigurationError, self._configuration.load)
        
        self._configuration._configurationCollection = None # Test for unmanaged repository
        self._configuration.load()
        
    def testStore(self):
        """ Tests the storing of the repository configuration. """
        
        self._configuration.store()
        
        self._dataModelHandlerMock.error = ConfigurationError("")
        self.assertRaises(ConfigurationError, self._configuration.store)
        
        self._configuration._configurationCollection = None # Test for unmanaged repository
        self._configuration.store()
        
    def testExists(self):
        """ Tests the existence check of the repository configuration. """
        
        self.assertFalse(self._configuration.exists())
        
        self._configurationCollectionMock.value = True
        self.assertTrue(self._configuration.exists())
        
        self._configurationCollectionMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._configuration.exists)
        
        self._configuration._configurationCollection = None # Test for unmanaged repository
        self.assertFalse(self._configuration.exists())

    def testDelete(self):
        """ Tests the deletion of the repository configuration. """
        
        self._configurationCollectionMock.value = True
        self._configuration.delete()
        
        self._configurationCollectionMock.value = False
        self._configuration.delete()
        
        self._configurationCollectionMock.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._configuration.delete)
        
        self._configuration._configurationCollection = None # Test for unmanaged repository
        self._configuration.delete()

    def testRelease(self):
        """ Tests the releasing of acquired resources of the repository configuration. """
        
        self._configuration.release()
        
        self._configurationCollectionMock.fileSystem.error = PersistenceError("")
        self.assertRaises(ConfigurationError, self._configuration.release)
        
        self._configuration._configurationCollection = None # Test for unmanaged repository
        self._configuration.release()

    def testManagedRepository(self):
        """ Tests the property flag which shows whether the configuration belongs to a managed repository or not. """ 
        
        self.assertTrue(self._configuration.isManagedRepository)
        
        self._configuration._configurationCollection = None # Test for unmanaged repository
        self.assertFalse(self._configuration.isManagedRepository)

    def testRepositoryConfigurationUrl(self):
        """ Tests the repository configuration URI property. """
        
        self.assertEquals(self._configurationCollectionMock.uri, self._configuration.repositoryConfigurationUri)
        
        self._configuration._configurationCollection = None # Test for unmanaged repository
        self.assertEquals(self._configuration.repositoryConfigurationUri, None)

    def testDefaultDataUris(self):
        """ Tests the default data URIs property. """
        
        self.assertEquals(self._configuration.defaultDataUris, self._dataStoreHandlerMock.defaultDataUris)
        
        self._configuration._configurationCollection = None # Test for unmanaged repository
        self.assertEquals(self._configuration.defaultDataUris, list())
