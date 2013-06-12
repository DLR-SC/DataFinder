# -*- coding: utf-8 -*-
#
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
Small integration test with a real SFTP server.
"""


import unittest

from datafinder.persistence.common import configuration
from datafinder.persistence import factory
import StringIO


__version__ = "$Revision-Id:$" 


_SERVER_URL = u"sftp://"
_USERNAME = None
_PASSWORD = None


@unittest.skipIf(_PASSWORD is None, "Not initialized.")
class SftpIntegrationTest(unittest.TestCase):
    """ Provides simple integration tests through the FileStorer interface. """
    # pylint: disable=R0904
    
    def setUp(self):
        bc = configuration.BaseConfiguration(_SERVER_URL, username=_USERNAME, password=_PASSWORD)
        self._fs = factory.FileSystem(bc)
        
    def testFileOperations(self):
        root = self._fs.createFileStorer("/")
        file1 = self._fs.createFileStorer(u"/fileä.txt")
        newFile = self._fs.createFileStorer(u"/fileä2.txt")
        self.assertEquals(len(root.getChildren()), 0)
        
        # Write and read some data
        file1.writeData(StringIO.StringIO("täst"))
        self.assertEquals(file1.readData().read(), "täst")
        self.assertTrue(file1.isLeaf)
        
        # Copy file
        file1.copy(newFile)
        self.assertEquals(newFile.readData().read(), "täst")
        
        # Cleaning up
        file1.delete()
        newFile.delete()
        self.assertFalse(file1.exists())
        self.assertFalse(newFile.exists())
        
    def testDirectoryOperations(self):
        # Setting it up
        collection = self._fs.createFileStorer(u"/päth/here/there")
        collection.createCollection(True)
        file1 = self._fs.createFileStorer(u"/päth/fileä.txt")
        file1.writeData(StringIO.StringIO(u"test2"))
        self.assertTrue(collection.isCollection)
        self.assertTrue(file1.isLeaf)
        orgCollection = self._fs.createFileStorer(u"/päth")
        newCollection = self._fs.createFileStorer(u"/päth2")
        
        # Moving it
        orgCollection.move(newCollection)
        self.assertTrue(newCollection.isCollection)
        self.assertFalse(orgCollection.exists())
        
        # Copying it
        newCollection.copy(orgCollection)
        self.assertTrue(newCollection.isCollection)
        self.assertTrue(orgCollection.exists())
        
        # Cleaning up
        orgCollection.delete()
        newCollection.delete()
        self.assertFalse(orgCollection.exists())
        self.assertFalse(newCollection.exists())
