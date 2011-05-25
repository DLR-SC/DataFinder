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

from datafinder.persistence.adapters.amazons3.data.adapter import DataS3Adapter
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock 


__version__ = "$Revision-Id$" 

    
class DataS3AdapterTestCase(TestCase):
    """ Tests the S3 - data adapter implementation. """
    
    def setUp(self):
        """ Creates default adapter usable by test cases. """
        
        self._defaultAdapter = DataS3Adapter("/path/identify", SimpleMock(SimpleMock(SimpleMock(SimpleMock(SimpleMock(SimpleMock(SimpleMock(SimpleMock()))))))), SimpleMock(SimpleMock()))
                
    def testisLeaf(self):
        """ Tests the normal behavior of the isLeaf method. """

        adapter = DataS3Adapter("identifier", SimpleMock(SimpleMock()), SimpleMock() )
        self.assertTrue(adapter.isLeaf)
        adapter = DataS3Adapter("", SimpleMock(SimpleMock()), SimpleMock())
        self.assertTrue(adapter.isLeaf)
        adapter = DataS3Adapter("/", SimpleMock(SimpleMock()), '')
        self.assertFalse(adapter.isLeaf)
        
    def testisCollection(self):
        """ Tests the normal behavior of the isResource method. """
        
        adapter = DataS3Adapter("/", SimpleMock(SimpleMock()), SimpleMock())
        self.assertTrue(adapter.isCollection)
        adapter = DataS3Adapter("identifier", SimpleMock(SimpleMock()), '')
        self.assertFalse(adapter.isCollection)

    def testcreateResource(self):
        """ Tests the normal behavior of the createResource createKey method."""     
        
        self._defaultAdapter.createResource()
        adapter = DataS3Adapter("", SimpleMock(SimpleMock(SimpleMock(error=PersistenceError("")))), '')
        self.assertRaises(PersistenceError, adapter.createResource)
    
    def testcreateCollection(self):
        """ Tests the normal behavior of the createCollection method. """
        
        adapter = DataS3Adapter("/identifier", SimpleMock(SimpleMock(SimpleMock(error=PersistenceError("")))) \
                                , SimpleMock())
        self.assertRaises(PersistenceError, adapter._getBucket())
        
    def testgetChildren(self):
        """ Tests the normal behavior of the getChildren method. """
    
        adapter = DataS3Adapter("/identifier", SimpleMock(SimpleMock(SimpleMock(SimpleMock(keyset = 1)))), SimpleMock())
        self.assertEquals(adapter.getChildren(), list())
        adapter = DataS3Adapter("/", SimpleMock(SimpleMock(SimpleMock(returnValue = []))), SimpleMock())
        self.assertEquals(adapter.getChildren(), list())
    
    def testwriteData(self):
        """ Tests the normal behavior of the writeData method. """
        
        self._defaultAdapter.writeData("Testen")
        
    def testreadData (self):
        """ Tests the normal behavior of the readData method. """

        adapter = DataS3Adapter("identifier", SimpleMock(SimpleMock(SimpleMock(SimpleMock()))), SimpleMock())
        fileObject = adapter.readData()
        self.assertEquals(fileObject.read(), "")
        
    def testdelete (self):
        """ Tests the normal behavior of the delete method. """
        
        self._defaultAdapter.delete()

    def testmove(self):
        """ Tests the normal behavior of the move method. """
                
        destinationBucket = SimpleMock(SimpleMock(SimpleMock()))
        self._defaultAdapter.move(destinationBucket)
        
    def testcopy(self):
        """ Tests the normal behavior of the copy method. """
        
        destinationBucket = SimpleMock(SimpleMock(SimpleMock(SimpleMock())))
        self._defaultAdapter.copy(destinationBucket)
        
    def testexists(self):
        """ Tests the normal behavior of the exists method. """
        
        adapter = DataS3Adapter("/anotherIdentifier", SimpleMock(SimpleMock(SimpleMock(SimpleMock()))), SimpleMock())
        self.assertTrue(adapter.exists())
        adapter = DataS3Adapter("/anotherIdentifier", SimpleMock(SimpleMock(SimpleMock())), "" )
        self.assertFalse(adapter.exists())
        adapter = DataS3Adapter("/anotherIdentifier", SimpleMock(SimpleMock(SimpleMock(error=PersistenceError("")))), SimpleMock())
        self.assertRaises(PersistenceError, adapter.exists)
