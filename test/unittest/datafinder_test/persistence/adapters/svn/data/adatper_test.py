# pylint: disable=W0511
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


import unittest

from io import StringIO

from datafinder.persistence.adapters.svn.data import adapter
from datafinder.persistence.adapters.svn.data.adapter import DataSubversionAdapter
from datafinder.persistence.adapters.svn.error import SubversionError
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock 


__version__ = "$Revision-Id:$" 


class _OsModuleMock(SimpleMock):
    """ Mocks the relevant functions of the os module. """
    
    def __init__(self, pathMock, returnValue=None, error=None):
        """ Constructor. """
        
        SimpleMock.__init__(self, returnValue, error)
        self.returnValue = returnValue
        self.error = error
        self.path = pathMock
        
    @staticmethod
    def strerror(errorNumber):
        """ Explicitly mocking the error interpretation function. """
        
        return str(errorNumber)


class _OpenMock(object):
    """ Mocks the built-in open function. """
    
    def __init__(self):
        """ Constructor. """
        
        self.error = False
        
    def __call__(self, *_, **__):
        """ Emulates the call to the open function. """
        
        if self.error:
            raise IOError("")
        else:
            return StringIO("")

    
class DataSubversionAdapterTestCase(unittest.TestCase):
    """ Tests the SVN - data adapter implementation. """
    
    def setUp(self):
        """ Creates test setup. """
        
        self._osPathMock = SimpleMock()
        self._osModuleMock = _OsModuleMock(self._osPathMock)
        adapter.os = self._osModuleMock
        self._openMock = _OpenMock()
        self._connectionMock = SimpleMock()
        self._defaultAdapter = DataSubversionAdapter("/path/identify", SimpleMock(self._connectionMock))
           
    def testLinkTarget(self):
        """ Tests the link target property. """
        
        self._connectionMock = SimpleMock(methodNameResultMap={"update": (None, None), "getProperty": ("/thelinkTargetPath", None)})
        adapter = DataSubversionAdapter("/identifier.txt", SimpleMock(self._connectionMock))
        self.assertEquals(adapter.linkTarget, "/thelinkTargetPath")
        self.assertTrue(adapter.isLink)
        self._connectionMock = SimpleMock(methodNameResultMap={"update": (None, None), "getProperty": (None, SubversionError)})
        adapter = DataSubversionAdapter("/identifier.txt", SimpleMock(self._connectionMock))
        self.assertEquals(adapter.linkTarget, None)
        self.assertFalse(adapter.isLink)
                
    def testIsLeaf(self):
        """ Tests the normal behavior of the isLeaf method. """

        self._connectionMock.value = True
        adapter = DataSubversionAdapter("/identifier.txt", SimpleMock(self._connectionMock))
        self.assertTrue(adapter.isLeaf)
        self._connectionMock.value = False
        adapter = DataSubversionAdapter("", SimpleMock(self._connectionMock))
        self.assertFalse(adapter.isLeaf)
        
    def testIsCollection(self):
        """ Tests the normal behavior of the isResource method. """
        
        self._connectionMock.value = True
        adapter = DataSubversionAdapter("/identifier", SimpleMock(self._connectionMock))
        self.assertTrue(adapter.isCollection)
        self._connectionMock.value = False
        adapter = DataSubversionAdapter("", SimpleMock(self._connectionMock))
        self.assertFalse(adapter.isCollection)

    def testCreateResource(self):
        """ Tests the normal behavior of the createResource createKey method."""     
        
        openFunction = globals()["__builtins__"]["open"]
        try:
            globals()["__builtins__"]["open"] = self._openMock
            self._openMock.error = False
            self._connectionMock = SimpleMock(repoWorkingCopyPath = "", methodNameResultMap={"add": (None, None), "checkin": (None, None)})
            adapter = DataSubversionAdapter("/identifier.txt", SimpleMock(self._connectionMock))
            adapter.createResource()
        
            self._openMock.error = True
            self.assertRaises(PersistenceError, adapter.createResource)
        finally:
            globals()["__builtins__"]["open"] = openFunction
    
    def testCreateCollection(self):
        """ Tests the normal behavior of the createCollection method. """
        
        self._osModuleMock.error = None
        self._connectionMock = SimpleMock(repoWorkingCopyPath = "", methodNameResultMap={"add": (None, None), "checkin": (None, None)})
        adapter = DataSubversionAdapter("/anotherIdentifier", SimpleMock(self._connectionMock))
        adapter.createCollection()
        self._osPathMock.value = True
        adapter.createCollection(True)
        
        self._osModuleMock.error = OSError("")
        self.assertRaises(PersistenceError, adapter.createCollection)
        
    def testGetChildren(self):
        """ Tests the normal behavior of the getChildren method. """
    
        self._connectionMock.value = ["/trunk/test/test.txt"]
        adapter = DataSubversionAdapter("/identifier", SimpleMock(self._connectionMock))
        self.assertEquals(["/trunk/test/test.txt"], adapter.getChildren())
    
    def testWriteData(self):
        """ Tests the normal behavior of the writeData method. """
        
        openFunction = globals()["__builtins__"]["open"]
        try:
            globals()["__builtins__"]["open"] = self._openMock
            self._openMock.error = False
            self._connectionMock = SimpleMock(repoWorkingCopyPath = "", methodNameResultMap={"update": (None, None)})
            adapter = DataSubversionAdapter("/anotherIdentifier", SimpleMock(self._connectionMock))
            adapter.writeData(StringIO(""))
        
            self._openMock.error = True
            self.assertRaises(PersistenceError, adapter.writeData, StringIO(""))
        finally:
            globals()["__builtins__"]["open"] = openFunction
        
    def testReadData (self):
        """ Tests the normal behavior of the readData method. """

        openFunction = globals()["__builtins__"]["open"]
        try:
            globals()["__builtins__"]["open"] = self._openMock
            self._openMock.error = False
            self._connectionMock = SimpleMock(repoWorkingCopyPath = "", methodNameResultMap={"update": (None, None)})
            adapter = DataSubversionAdapter("/anotherIdentifier", SimpleMock(self._connectionMock))
            adapter.readData()
        
            self._openMock.error = True
            self.assertRaises(PersistenceError, adapter.readData)
        finally:
            globals()["__builtins__"]["open"] = openFunction
        
    def testDelete (self):
        """ Tests the normal behavior of the delete method. """
        
        self._connectionMock = SimpleMock(repoWorkingCopyPath = "", methodNameResultMap={"update": (None, None), "delete": (None, None), "checkin": (None, None)})
        adapter = DataSubversionAdapter("/anotherIdentifier", SimpleMock(self._connectionMock))
        adapter.delete()
        
        self._connectionMock = SimpleMock(repoWorkingCopyPath = "", methodNameResultMap={"update": (None, None), "delete": (None, SubversionError), "checkin": (None, None)})
        adapter = DataSubversionAdapter("/anotherIdentifier", SimpleMock(self._connectionMock))
        self.assertRaises(PersistenceError, adapter.delete)

    def testMove(self):
        """ Tests the normal behavior of the move method. """
                
        destination = DataSubversionAdapter("/anotherIdentifier", SimpleMock(self._connectionMock))
        self._connectionMock = SimpleMock(repoWorkingCopyPath = "", methodNameResultMap={"update": (None, None), "copy": (None, None), "checkin": (None, None), "delete": (None, None)})
        adapter = DataSubversionAdapter("identifier", SimpleMock(self._connectionMock))
        adapter.move(destination)
        
        self._connectionMock = SimpleMock(repoWorkingCopyPath = "", methodNameResultMap={"update": (None, None), "copy": (None, SubversionError), "checkin": (None, None), "delete": (None, None)})
        adapter = DataSubversionAdapter("identifier", SimpleMock(self._connectionMock))
        self.assertRaises(PersistenceError, adapter.move, destination)
        
    def testCopy(self):
        """ Tests the normal behavior of the copy method. """
        
        destination = DataSubversionAdapter("/anotherIdentifier", SimpleMock(self._connectionMock))
        self._connectionMock = SimpleMock(repoWorkingCopyPath = "", methodNameResultMap={"update": (None, None), "copy": (None, None), "checkin": (None, None)})
        adapter = DataSubversionAdapter("identifier", SimpleMock(self._connectionMock))
        adapter.copy(destination)
        
        self._connectionMock = SimpleMock(repoWorkingCopyPath = "", methodNameResultMap={"update": (None, None), "copy": (None, SubversionError), "checkin": (None, None)})
        adapter = DataSubversionAdapter("identifier", SimpleMock(self._connectionMock))
        self.assertRaises(PersistenceError, adapter.copy, destination)
        
    def testExists(self):
        """ Tests the normal behavior of the exists method. """
        
        self._osPathMock.value = True
        self._connectionMock = SimpleMock(repoWorkingCopyPath = "", methodNameResultMap={"update": (None, None)})
        adapter = DataSubversionAdapter("/anotherIdentifier", SimpleMock(self._connectionMock))
        self.assertTrue(adapter.exists()) 
        self._osPathMock.value = False
        self._connectionMock = SimpleMock(repoWorkingCopyPath = "", methodNameResultMap={"update": (None, None)})
        adapter = DataSubversionAdapter("/anotherIdentifier", SimpleMock(self._connectionMock))
        self.assertFalse(adapter.exists())
        self._connectionMock = SimpleMock(repoWorkingCopyPath = "", methodNameResultMap={"update": (None, SubversionError)})
        adapter = DataSubversionAdapter("/anotherIdentifier", SimpleMock(self._connectionMock))
        self.assertRaises(PersistenceError, adapter.exists)
        