#
# Created: 31.07.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: filestorer_test.py 4468 2010-02-22 13:40:12Z meinel $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


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


__version__ = "$LastChangedRevision: 4468 $"


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
        self.assertEquals(self._fileStorer.metadataSearch([]), self._metadataStorer.search([]))
        
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
