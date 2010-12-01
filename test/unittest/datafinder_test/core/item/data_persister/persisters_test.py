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
Tests the different data persister implementations.
"""


import unittest

from datafinder.core.configuration.properties.constants import ARCHIVE_PART_COUNT_ID, CONTENT_IDENTIFIER_ID
from datafinder.core.error import AuthenticationError, ItemError
from datafinder.core.item.data_persister import persisters
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class DefaultDataPersisterTestCase(unittest.TestCase):
    """ Tests the default data persister. """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._fileStorerMock = SimpleMock()
        self._persister = persisters.DefaultDataPersister("dataState", self._fileStorerMock)
        
    def testRetrieveData(self):
        """ DefaultDataPersisterTestCase: Tests the retrieval of data. """
        
        self._persister.retrieveData()
        
        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._persister.retrieveData)
        
    def testStoreData(self):
        """ DefaultDataPersisterTestCase: Tests the retrieval of data. """
        
        self._persister.storeData(SimpleMock())
        
        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._persister.storeData, SimpleMock())


class FlatDataPersisterTestCase(unittest.TestCase):
    """ Tests the flat data persister. """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._fileStorerMock = SimpleMock()
        self._itemMock = SimpleMock(uri="", properties={CONTENT_IDENTIFIER_ID:SimpleMock(value="")})
        self._propertyRegistryMock = SimpleMock(SimpleMock())
        self._testAccessCallback = SimpleMock()
        self._persister = persisters.FlatDataPersister("dataState", SimpleMock(), self._itemMock, 
                                                       self._propertyRegistryMock, self._testAccessCallback)
        self._persister._fileStorer = self._fileStorerMock
        
    def testCreate(self):
        """ FlatDataPersisterTestCase: Tests the additional actions performed during creation. """
        
        self._persister.create()

        self._fileStorerMock.value = True
        self.assertRaises(ItemError, self._persister.create)
   
        self._fileStorerMock.value = False
        self._itemMock.properties = dict()
        self.assertRaises(ItemError, self._persister.create)
   
        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._persister.create)

        self._testAccessCallback.error = AuthenticationError("", None, None)
        self.assertRaises(AuthenticationError, self._persister.create)
        
    def testDelete(self):
        """ FlatDataPersisterTestCase: Tests the deletion. """
        
        self._persister.delete()
        
        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._persister.delete)

        self._testAccessCallback.error = AuthenticationError("", None, None)
        self.assertRaises(AuthenticationError, self._persister.delete)
        
    def testCopy(self):
        """ FlatDataPersisterTestCase: Tests the additional actions performed during copying. """
        
        itemMock = SimpleMock(uri="test", 
                              properties={CONTENT_IDENTIFIER_ID:None})
        self._persister.copy(itemMock)
        
        itemMock.properties = dict()
        self.assertRaises(ItemError, self._persister.copy, itemMock)
        
        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._persister.copy, itemMock)

        self._testAccessCallback.error = AuthenticationError("", None, None)
        self.assertRaises(AuthenticationError, self._persister.copy, itemMock)


class HierarchicalDataPersisterTestCase(unittest.TestCase):
    """ Tests the hierarchical data persister. """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._fileStorerMock = SimpleMock(parent=SimpleMock([SimpleMock()], identifier="/test"))
        self._testAccessCallback = SimpleMock()
        self._persister = persisters.HierarchicalDataPersister("dataState", self._fileStorerMock, self._testAccessCallback)
        
    def testCreate(self):
        """ HierarchicalDataPersisterTestCase: Tests the additional actions performed during creation. """
        
        self._persister.create()
        
        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._persister.create)
        
        self._testAccessCallback.error = AuthenticationError("", None, None)
        self.assertRaises(AuthenticationError, self._persister.create)
        
    def testDelete(self):
        """ HierarchicalDataPersisterTestCase: Tests the deletion. """
        
        # deletion without deletion of parent directories
        self._persister.delete()
        
        # deletion wit deletion of parent directories
        self._fileStorerMock.parent.value = list()
        self._fileStorerMock.parent.parent = SimpleMock(list(), name="")
        self._persister.delete()
        
        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._persister.delete)
        
        self._testAccessCallback.error = AuthenticationError("", None, None)
        self.assertRaises(AuthenticationError, self._persister.delete)

    def testCopy(self):
        """ HierarchicalDataPersisterTestCase: Tests the additional actions performed during copying. """
        
        itemMock = SimpleMock(dataPersister=SimpleMock(fileStorer=SimpleMock(parent=SimpleMock())))
        self._persister.copy(itemMock)
        
        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._persister.copy, itemMock)

        self._testAccessCallback.error = AuthenticationError("", None, None)
        self.assertRaises(AuthenticationError, self._persister.copy, itemMock)

    def testMove(self):
        """ HierarchicalDataPersisterTestCase: Tests the additional actions performed during move operations. """
        
        itemMock = SimpleMock(dataPersister=SimpleMock(fileStorer=SimpleMock(parent=SimpleMock())))
        self._persister.move(itemMock)
        
        self._fileStorerMock.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._persister.move, itemMock)

        self._testAccessCallback.error = AuthenticationError("", None, None)
        self.assertRaises(AuthenticationError, self._persister.move, itemMock)


class ArchivePersisterTestCase(unittest.TestCase):
    """ Tests the archive data persister. """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._fileStorerMock = SimpleMock(name="base", parent=SimpleMock(SimpleMock()))
        self._itemMock = SimpleMock(dataUri="/aasdsad", properties={ARCHIVE_PART_COUNT_ID:SimpleMock(value=1)})
        self._baseDataPersisterMock = SimpleMock(fileStorer=self._fileStorerMock)
        self._persister = persisters.ArchiveDataPersister("dataState", self._itemMock, self._baseDataPersisterMock)
        
    def testCreate(self):
        """ Test creation method of the archive data persister. """
        
        self._persister.create()
        
        self._baseDataPersisterMock.error = ItemError("Already exists.")
        self.assertRaises(ItemError, self._persister.create)
        
    def testDelete(self):
        """ Test deletion method of the archive data persister. """
        
        self._persister.delete()
        
        self._persister._count = 2
        self._persister.delete()
        
    def testCopy(self):
        """ Test copy method of the archive data persister. """
        
        itemMock = SimpleMock(dataPersister=self._persister)
        self._persister._count = 2
        self._persister.copy(itemMock)
        
    def testMove(self):
        """ Test move method of the archive data persister. """
        
        itemMock = SimpleMock(dataUri="/aasdsad", dataPersister=self._persister)
        self._persister.move(itemMock)
        
        itemMock.dataUri = "/Peter/aasdsad"
        self._persister._count = 2
        self._persister.move(itemMock)
        
    def testRetrieveData(self):
        """ Test retrieveData method of the archive data persister. """
        
        self._persister.retrieveData()
        
        self._persister.retrieveData(2)
        
        self._fileStorerMock.parent.value.error = PersistenceError("Does not exist.")
        self.assertRaises(PersistenceError, self._persister.retrieveData, -1)

    def testStoreData(self):
        """ Test the storeData method of the archive persister. """
        
        self.assertEquals(self._itemMock.properties[ARCHIVE_PART_COUNT_ID].value, 1)
        self._persister.storeData(SimpleMock())
        self.assertEquals(self._itemMock.properties[ARCHIVE_PART_COUNT_ID].value, 2)
        
        self.assertEquals(self._itemMock.properties[ARCHIVE_PART_COUNT_ID].value, 2)
        self._fileStorerMock.parent.value.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._persister.storeData, SimpleMock())
        self.assertEquals(self._itemMock.properties[ARCHIVE_PART_COUNT_ID].value, 2)
