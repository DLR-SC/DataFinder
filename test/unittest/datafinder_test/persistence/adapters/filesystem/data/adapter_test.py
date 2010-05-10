#pylint: disable-msg=R0904
# R0904: Does not make sense for a test case here.

# Created: 01.03.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: adapter_test.py 4394 2010-01-18 13:40:39Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements test cases of the data adapter.
"""


import unittest
import shutil
from StringIO import StringIO

from datafinder.persistence.adapters.filesystem.data import adapter
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4394 $"


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


class DataWebdavAdapterTestCase(unittest.TestCase):
    """ Implements test cases of the data adapter. """

    def setUp(self):
        """ Creates test setup. """
        
        self._osPathMock = SimpleMock()
        self._osModuleMock = _OsModuleMock(self._osPathMock)
        adapter.os = self._osModuleMock
        self._shutilMock = SimpleMock()
        adapter.shutil = self._shutilMock
        self._utilMock = SimpleMock()
        adapter.util = self._utilMock
        self._openMock = _OpenMock()
        self._identifierMapperMock = SimpleMock()
        
        self._adapter = adapter.DataFileSystemAdapter("/identifier", self._identifierMapperMock)

    def testLinkTarget(self):
        """ Tests the link target property. """
        
        self._osPathMock.value = False
        self._utilMock.value = SimpleMock(["C:\\test.txt"])
        self._identifierMapperMock.value = "/C:/test.txt"
        self.assertEquals("/C:/test.txt", self._adapter.linkTarget)
        self.assertTrue(self._adapter.isLink)
        
    def testIsLink(self):
        """ Tests the isLink method behavior. """
        
        self._utilMock.error = None
        self._utilMock.value = SimpleMock(True)
        self.assertTrue(self._adapter.isLink)
        
        self._utilMock.value = SimpleMock(False)
        self.assertFalse(self._adapter.isLink)
        
        self._utilMock.value = SimpleMock(error=PersistenceError(""))
        try:
            self.assertFalse(self._adapter.isLink)
            self.fail("PersistenceError not raised.")
        except PersistenceError:
            self.assertTrue(True)

    def testIsCollection(self):
        """ Tests the isCollection method behavior. """
        
        self._osPathMock.value = True
        self.assertTrue(self._adapter.isCollection)
        
        self._osPathMock.value = False
        self.assertFalse(self._adapter.isCollection)

    def testIsLeaf(self):
        """ Tests the isLeaf method behavior. """
        
        self._osPathMock.value = True
        self.assertTrue(self._adapter.isLeaf)
        
        self._osPathMock.value = False
        self.assertFalse(self._adapter.isLeaf)

    def testCanAddChildren(self):
        """ Tests the behavior of the canAddChildren flag. """
    
        self._osPathMock.value = True
        self._utilMock.value = False
        self.assertTrue(self._adapter.canAddChildren)
        
        self._utilMock.value = True
        self.assertFalse(self._adapter.canAddChildren)
        
    def testCreateCollection(self):
        """ Tests the createCollection method behavior. """
        
        self._osModuleMock.error = None
        self._adapter.createCollection()
        self._adapter.createCollection(True)
        
        self._osModuleMock.error = OSError("")
        self.assertRaises(PersistenceError, self._adapter.createCollection)
        
    def testCreateResource(self):
        """ Tests the createResource method behavior. """
        
        openFunction = globals()["__builtins__"]["open"]
        try:
            globals()["__builtins__"]["open"] = self._openMock
            self._openMock.error = False
            self._adapter.createResource()
        
            self._openMock.error = True
            self.assertRaises(PersistenceError, self._adapter.createResource)
        finally:
            globals()["__builtins__"]["open"] = openFunction

    def testCreateLink(self):
        """ Tests the createLink method behavior. """
        
        linkSource = adapter.DataFileSystemAdapter("", SimpleMock())
        
        self._utilMock.error = None
        self._utilMock.value = SimpleMock()
        self._adapter.createLink(linkSource)
        
        self._utilMock.value = SimpleMock(error=PersistenceError(""))
        self.assertRaises(PersistenceError, self._adapter.createLink, linkSource)
    
    def testGetChildren(self):
        """ Tests the getChildren method behavior. """
        
        self._osPathMock.value = True
        self._utilMock.error = None
        self._utilMock.value = ["C:\\test.txt"]
        self._identifierMapperMock.value = "/C:/test.txt"
        self.assertEquals(["/C:/test.txt"], self._adapter.getChildren())
        
        self._osPathMock.value = True
        self._utilMock.error = OSError("")
        self.assertRaises(PersistenceError, self._adapter.getChildren)
        
    def testExists(self):
        """ Tests the exists method behavior. """
        
        self._osPathMock.value = True
        self.assertTrue(self._adapter.exists())
        
        self._osPathMock.value = False
        self.assertFalse(self._adapter.exists())
        
    def testDelete(self):
        """ Tests the exists method behavior. """
        
        self._shutilMock.error = None
        self._osPathMock.value = True
        self._adapter.delete()
        
        self._shutilMock.error = OSError("")
        self.assertRaises(PersistenceError, self._adapter.delete)
        
        self._osModuleMock.error = None
        self._osPathMock.value = False
        self._adapter.delete()
        
        self._osModuleMock.error = OSError("")
        self.assertRaises(PersistenceError, self._adapter.delete)
        
    def testCopy(self):
        """ Tests the copy method behavior. """
        
        destination = adapter.DataFileSystemAdapter("", SimpleMock())
        
        self._shutilMock.error = None
        self._adapter.copy(destination)
        
        self._shutilMock.error = IOError("")
        self.assertRaises(PersistenceError, self._adapter.copy, destination)
        
        self._shutilMock.error = OSError("")
        self.assertRaises(PersistenceError, self._adapter.copy, destination)
        
        self._shutilMock.error = shutil.Error("")
        self.assertRaises(PersistenceError, self._adapter.copy, destination)
        
    def testMove(self):
        """ Tests the move method behavior. """
        
        destination = adapter.DataFileSystemAdapter("", SimpleMock())
        
        self._osModuleMock.error = None
        self._adapter.move(destination)
        
        self._osModuleMock.error = OSError("")
        self.assertRaises(PersistenceError, self._adapter.move, destination)
        
    def testReadData(self):
        """ Tests the readData method behavior. """
        
        openFunction = globals()["__builtins__"]["open"]
        try:
            globals()["__builtins__"]["open"] = self._openMock
            self._openMock.error = False
            self._adapter.readData()
        
            self._openMock.error = True
            self.assertRaises(PersistenceError, self._adapter.readData)
        finally:
            globals()["__builtins__"]["open"] = openFunction

    def testWriteData(self):
        """ Tests the writeData method behavior. """
        
        openFunction = globals()["__builtins__"]["open"]
        try:
            globals()["__builtins__"]["open"] = self._openMock
            self._openMock.error = False
            self._adapter.writeData(StringIO(""))
        
            self._openMock.error = True
            self.assertRaises(PersistenceError, self._adapter.writeData, StringIO(""))
        finally:
            globals()["__builtins__"]["open"] = openFunction
