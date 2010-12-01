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
Tests the repository configuration.
"""


import unittest

from datafinder.core.configuration import configuration
from datafinder.core.error import ConfigurationError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


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
