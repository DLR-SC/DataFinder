# pylint: disable-msg=W0511
# Created: 28.11.2009  ney <Miriam.Ney@dlr.de>
# Changed: $Id: adapter_test.py 4417 2010-01-28 10:57:55Z ney_mi $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests the data adapter implementation.
"""


import unittest


from datafinder.persistence.adapters.amazonS3.data.adapter import DataS3Adapter
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock 


_PROPERTY_NOT_FOUND_MESSAGE = "Property is missing:"

__version__ = "$LastChangedRevision: 4417 $"

    
class DataS3AdapterTestCase(unittest.TestCase):
    """ Tests the S3 - data adapter implementation. """
    
    def setUp(self):
        """ Creates default adapter usable by test cases. """
        
        self._defaultAdapter = DataS3Adapter("/path/identify", SimpleMock(SimpleMock(SimpleMock(SimpleMock()))), SimpleMock(), SimpleMock())
                
    def testisLeaf(self):
        """ Tests the normal behavior of the isLeaf method. """

        adapter = DataS3Adapter("identifier", SimpleMock(), SimpleMock(), SimpleMock())
        self.assertTrue(adapter.isLeaf)
        adapter = DataS3Adapter("identifier", SimpleMock(), SimpleMock(), '')
        self.assertFalse(adapter.isLeaf)
        adapter = DataS3Adapter("identifier", SimpleMock(), '', SimpleMock())
        self.assertFalse(adapter.isLeaf)
        
    def testisCollection(self):
        """ Tests the normal behavior of the isResource method. """
        
        adapter = DataS3Adapter("identifier", SimpleMock(), SimpleMock(), '')
        self.assertTrue(adapter.isCollection)
        adapter = DataS3Adapter("identifier", SimpleMock(), '', '')
        self.assertFalse(adapter.isCollection)

    def testcreateResource(self):
        """ Tests the normal behavior of the createResource createKey method."""     
        
        self._defaultAdapter.createResource()
        adapter = DataS3Adapter("identifier", SimpleMock(SimpleMock()), '', '')
        self.assertRaises(PersistenceError, adapter.createResource)
    
    def testcreateCollection(self):
        """ Tests the normal behavior of the createCollection method. """
        
        self._defaultAdapter.createCollection()
        adapter = DataS3Adapter("identifier", SimpleMock(SimpleMock()), '', '')
        self.assertRaises(PersistenceError, adapter.createCollection)
        
    def testgetChildren(self):
        """ Tests the normal behavior of the getChildren method. """
    
        adapter = DataS3Adapter("/identifier", SimpleMock(SimpleMock(SimpleMock(SimpleMock(keyset = 1)))), SimpleMock(), SimpleMock())
        self.assertEquals(adapter.getChildren(), 1)
    
    def testwriteData(self):
        """ Tests the normal behavior of the writeData method. """
        self._defaultAdapter.writeData("Testen")
        
    def testreadData (self):
        """ Tests the normal behavior of the readData method. """

        adapter = DataS3Adapter("identifier", SimpleMock(SimpleMock(SimpleMock(SimpleMock()))), SimpleMock(), SimpleMock())
        self.assertEquals(adapter.readData().read(), "")
        
    def testdelete (self):
        """ Tests the normal behavior of the delete method. """
        
        self._defaultAdapter.delete()
        

    def testmove(self):
        """ Tests the normal behavior of the move method. """
                
        destinationBucket = SimpleMock(SimpleMock(SimpleMock()))
        destinationKey = SimpleMock(SimpleMock())
        #source = DataS3Adapter("/anotherIdentifier", SimpleMock(SimpleMock(SimpleMock(SimpleMock()))), SimpleMock(), SimpleMock())
        self._defaultAdapter.move(destinationBucket, destinationKey)
        
    def testcopy(self):
        """ Tests the normal behavior of the copy method. """
        destinationBucket = SimpleMock(SimpleMock(SimpleMock()))
        destinationKey = SimpleMock()
        self._defaultAdapter.copy(destinationBucket, destinationKey)
        
    def testexists(self):
        """ Tests the normal behavior of the exists method. """
        
        adapter = DataS3Adapter("/anotherIdentifier", SimpleMock(SimpleMock(SimpleMock())), SimpleMock(), SimpleMock())
        self.assertTrue(adapter.exists())
        adapter = DataS3Adapter("/anotherIdentifier", SimpleMock(SimpleMock()), "" , SimpleMock())
        self.assertFalse(adapter.exists())
        adapter = DataS3Adapter("/anotherIdentifier", SimpleMock(error=PersistenceError("")), SimpleMock(), SimpleMock())
        self.assertRaises(PersistenceError, adapter.exists)
