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
Implements tests for the file storer.
"""


import unittest
from StringIO import StringIO

from datafinder.persistence.factory import FileSystem
from datafinder.persistence import filestorer
from datafinder.persistence.data.datastorer import NullDataStorer
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata.metadatastorer import NullMetadataStorer
from datafinder.persistence.privileges.privilegestorer import NullPrivilegeStorer
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class FileStorerTestCase(unittest.TestCase):
    """ Implements test cases for the file storer. """
    
    def setUp(self):
        """ Creates the object under test. """
        
        self._nullFileSystem = FileSystem(None)
        self._dataStorer = NullDataStorer("/identifier")
        self._metadataStorer = NullMetadataStorer("/identifier")
        self._privilegeStorer = NullPrivilegeStorer("/identifier")
        self._fileStorer = filestorer.FileStorer(self._nullFileSystem, "/identifier", self._dataStorer, 
                                                 self._metadataStorer, self._privilegeStorer)
        self._destFileStorer = filestorer.FileStorer(self._nullFileSystem, "/identifier", self._dataStorer, 
                                                     self._metadataStorer, self._privilegeStorer)
    
    def testBasicInterface(self):
        """ Just invokes the public interface and ensures the call is delegated accordingly. """ 
                
        self.assertEquals(self._fileStorer.name, "identifier")
        self.assertEquals(self._fileStorer.identifier, "/identifier")
        self.assertEquals(self._fileStorer.uri, None)
        self.assertEquals(self._fileStorer.parent.identifier, "/")
        self.assertEquals(self._fileStorer.linkTarget, None)
        self.assertEquals(self._fileStorer.fileSystem, self._nullFileSystem)
        self.assertEquals(self._fileStorer.dataStorer, self._dataStorer)
        self.assertEquals(self._fileStorer.metadataStorer, self._metadataStorer)
        self.assertEquals(self._fileStorer.privilegeStorer, self._privilegeStorer)
        
        self.assertEquals(self._fileStorer.isCollection, self._dataStorer.isCollection)
        self.assertEquals(self._fileStorer.isLeaf, self._dataStorer.isLeaf)
        self.assertEquals(self._fileStorer.isLink, self._dataStorer.isLink)
        self.assertEquals(self._fileStorer.isCollection, self._dataStorer.isCollection)
        self.assertEquals(self._fileStorer.canAddChildren, self._dataStorer.canAddChildren)
        self.assertEquals(self._fileStorer.createLink(self._destFileStorer), self._dataStorer.createLink(self._dataStorer))
        self.assertEquals(self._fileStorer.createResource(), self._dataStorer.createResource())
        self.assertEquals(self._fileStorer.delete(), self._dataStorer.delete())
        self.assertEquals(self._fileStorer.copy(self._destFileStorer), self._dataStorer.copy(self._dataStorer))
        self.assertEquals(self._fileStorer.move(self._destFileStorer), self._dataStorer.move(self._dataStorer))
        self.assertEquals(self._fileStorer.getChildren(), self._dataStorer.getChildren())
        self.assertEquals(self._fileStorer.exists(), self._dataStorer.exists())
        self.assertEquals(self._fileStorer.readData().read(), self._dataStorer.readData().read())
        self.assertEquals(self._fileStorer.writeData(StringIO("")), self._dataStorer.writeData(StringIO("")))
        
        self.assertEquals(self._fileStorer.retrieveMetadata([]), self._metadataStorer.retrieve([]))
        self.assertEquals(self._fileStorer.updateMetadata([]), self._metadataStorer.update(dict()))
        self.assertEquals(self._fileStorer.deleteMetadata([]), self._metadataStorer.delete([]))
        
        self.assertEquals(self._fileStorer.updateAcl(list()), self._privilegeStorer.updateAcl(list()))
        self.assertEquals(self._fileStorer.retrievePrivileges(), self._privilegeStorer.retrievePrivileges())
        self.assertEquals(self._fileStorer.retrieveAcl(), self._privilegeStorer.retrieveAcl())

    def testGetTemporaryFileObject(self):
        """ Tests the creation of the temporary file object. """
        
        expectedName = "/temp/tempfile"
        expectedFile = StringIO("TestContent")
        mkstempMock = SimpleMock((expectedFile, expectedName))
        fdOpenMock = SimpleMock(expectedFile)
        namedTemporaryFileMock = SimpleMock(name=expectedName, file=expectedFile)
        filestorer.mkstemp = mkstempMock
        filestorer.os.fdopen = fdOpenMock
        filestorer.NamedTemporaryFile = SimpleMock(namedTemporaryFileMock)
        self._fileStorer.readData = SimpleMock(StringIO("Some test data."))
        
        self._fileStorer._tempfile = None
        self.assertEquals(self._fileStorer.getTemporaryFileObject(), (expectedName, expectedFile))
        
        #self._fileStorer._tempfile = None
        #self._fileStorer.readData = SimpleMock(StringIO("Some test data."))
        #namedTemporaryFileMock.error = IOError("")
        #self.assertRaises(PersistenceError, self._fileStorer.getTemporaryFileObject)
        
        self._fileStorer._tempfile = None
        self._fileStorer.readData = SimpleMock(StringIO("Some test data."))
        self.assertEquals(self._fileStorer.getTemporaryFileObject("", False), (expectedName, expectedFile))
        
        self._fileStorer._tempfile = None
        self._fileStorer.readData = SimpleMock(StringIO("Some test data."))
        mkstempMock.error = IOError("")
        self.assertRaises(PersistenceError, self._fileStorer.getTemporaryFileObject, "", False)
