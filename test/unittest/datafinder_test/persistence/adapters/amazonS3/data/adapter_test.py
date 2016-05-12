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
Tests the data adapter implementation.
"""


from unittest import TestCase

from boto.exception import S3ResponseError
from datafinder.persistence.adapters.amazonS3.data.adapter import DataS3Adapter, _cleanupTemporaryFile, _temporaryFiles
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock 


__version__ = "$Revision-Id$" 

    
class DataS3AdapterTestCase(TestCase):
    """ Tests the S3 - data adapter implementation. """
    
    def setUp(self):
        """ Creates default adapter usable by test cases."""
        
        self._defaultAdapter = DataS3Adapter("/path/identify", SimpleMock(SimpleMock(SimpleMock(SimpleMock(SimpleMock(SimpleMock(SimpleMock(SimpleMock()))))))), SimpleMock(SimpleMock()))
        self.responseError = S3ResponseError("","","")
                       
    def testGetBucket(self):
        """ Tests the getBucket method"""
        
        #failure look up
        try:
            self.assertRaises(PersistenceError, DataS3Adapter("identifier", SimpleMock(SimpleMock(error=self.responseError)), ''))
            self.fail("PersistenceError not thrown")
        except PersistenceError:
            self.assertTrue(True)
        #failure create
        try:
            self.assertRaises(PersistenceError, DataS3Adapter("identifier", SimpleMock(SimpleMock(returnValue = None, error = self.responseError)), ''))
            self.fail("PersistenceError not thrown")
        except PersistenceError:
            self.assertTrue(True)
            
    def testIsLeaf(self):
        """ Tests the normal behavior of the isLeaf method. """
        
        #true
        adapter = DataS3Adapter("identifier", SimpleMock(SimpleMock()), SimpleMock() )
        self.assertTrue(adapter.isLeaf)
        adapter = DataS3Adapter("", SimpleMock(SimpleMock()), SimpleMock())
        self.assertTrue(adapter.isLeaf)
        #false
        adapter = DataS3Adapter("/", SimpleMock(SimpleMock()), '')
        self.assertFalse(adapter.isLeaf)
        
    def testIsCollection(self):
        """ Tests the normal behavior of the isResource method. """
        
        #true
        adapter = DataS3Adapter("/", SimpleMock(SimpleMock()), SimpleMock())
        self.assertTrue(adapter.isCollection)
        #false
        adapter = DataS3Adapter("identifier", SimpleMock(SimpleMock()), '')
        self.assertFalse(adapter.isCollection)
       
    def testCanAddChildren(self):
        """" Tests the property to add children """
        
        #false
        self.assertFalse(self._defaultAdapter.canAddChildren)
    
    def testCreateResource(self):
        """ Tests the normal behavior of the createResource createKey method."""  
           
        #success
        self._defaultAdapter.createResource()
        #failure
        adapter = DataS3Adapter("", SimpleMock(SimpleMock(SimpleMock(error=self.responseError))), '')
        try:
            adapter.createResource()
            self.fail("PersistenceError not thrown")
        except PersistenceError:
            self.assertTrue(True)
            
    def testGetChildren(self):
        """ Tests the normal behavior of the getChildren method. """
        
        #success
        adapter = DataS3Adapter("/identifier", SimpleMock(SimpleMock(SimpleMock(SimpleMock(keyset = 1)))), SimpleMock())
        self.assertEquals(adapter.getChildren(), list())
        adapter = DataS3Adapter("/", SimpleMock(SimpleMock(SimpleMock(returnValue = []))), SimpleMock())
        self.assertEquals(adapter.getChildren(), list())
        #failure
        adapter = DataS3Adapter("/", SimpleMock(SimpleMock(SimpleMock(error=self.responseError))), SimpleMock())
        try:
            adapter.getChildren()
            self.fail("PersistenceError not thrown")
        except PersistenceError:
            self.assertTrue(True)
        
    def testWriteData(self):
        """ Tests the normal behavior of the writeData method. """
        
        #success
        self._defaultAdapter.writeData("Testen")
        #failure
        adapter = DataS3Adapter("", SimpleMock(SimpleMock(SimpleMock(error=self.responseError))), '')
        try:
            adapter.writeData("Testen")
            self.fail("PersistenceError not thrown")
        except PersistenceError:
            self.assertTrue(True)
        
    def testReadData (self):
        """ Tests the normal behavior of the readData method. """
        
        #success
        adapter = DataS3Adapter("identifier", SimpleMock(SimpleMock(SimpleMock(SimpleMock()))), SimpleMock())
        fileObject = adapter.readData()
        self.assertEquals(fileObject.read(), "")
        
    def testDelete (self):
        """ Tests the normal behavior of the delete method. """
        
        #success
        self._defaultAdapter.delete()
        #failure
        adapter = DataS3Adapter("/anotherIdentifier", SimpleMock(SimpleMock(SimpleMock(error=self.responseError))), SimpleMock())
        try: 
            adapter.delete()
            self.fail("PersistenceError not thrown")
        except PersistenceError:
            self.assertTrue(True)
        #failure: is not leaf
        adapter = DataS3Adapter("/", SimpleMock(SimpleMock(SimpleMock(error=self.responseError))), SimpleMock())
        try: 
            adapter.delete()
            self.fail("PersistenceError not thrown")
        except PersistenceError:
            self.assertTrue(True)
            
    def testMove(self):
        """ Tests the normal behavior of the move method. """
        
        #success        
        destinationBucket = SimpleMock(SimpleMock(SimpleMock()))
        self._defaultAdapter.move(destinationBucket)
        
    def testCopy(self):
        """ Tests the normal behavior of the copy method. """
        
        #success
        destinationBucket = SimpleMock(SimpleMock(SimpleMock(SimpleMock())))
        self._defaultAdapter.copy(destinationBucket)
        #failure
        adapter = DataS3Adapter("/anotherIdentifier", SimpleMock(SimpleMock(SimpleMock(error=self.responseError))), SimpleMock())
        try:
            adapter.copy(destinationBucket)
            self.fail("PersistenceError not thrown")
        except PersistenceError:
            self.assertTrue(True)
        
    def testExists(self):
        """ Tests the normal behavior of the exists method. """
        
        #exists
        adapter = DataS3Adapter("/anotherIdentifier", SimpleMock(SimpleMock(SimpleMock(SimpleMock()))), SimpleMock())
        self.assertTrue(adapter.exists())
        #does not exist
        adapter = DataS3Adapter("/anotherIdentifier", SimpleMock(SimpleMock(SimpleMock())), "" )
        self.assertFalse(adapter.exists())
        #error
        adapter = DataS3Adapter("/anotherIdentifier", SimpleMock(SimpleMock(SimpleMock(error=self.responseError))), SimpleMock())
        try:
            adapter.exists()
            self.fail("PersistenceError not thrown")
        except PersistenceError:
            self.assertTrue(True)
        
    def testCleanupTemporary(self):
        """ Testing the cleanup procedure """
        
        #success and failure
        files= list()
        files.append(SimpleMock(error = PersistenceError("")))
        _cleanupTemporaryFile(files)
            
