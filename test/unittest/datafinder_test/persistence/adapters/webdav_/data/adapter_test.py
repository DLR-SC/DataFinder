#pylint: disable-msg=R0904
# R0904: Does not make sense for a test case here.
#
#
# Created: 23.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: adapter_test.py 4394 2010-01-18 13:40:39Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests the data adapter implementation.
"""


__version__ = "$LastChangedRevision: 4394 $"


from StringIO import StringIO
import unittest

from webdav.Connection import WebdavError

from datafinder.persistence.adapters.webdav_.data.adapter import DataWebdavAdapter
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4394 $"


_VALID_GETCHILDREN_WEBDAV_RESULT = {"/Path": (True, None)}
_VALID_GETCHILDREN_RESULT = ["/Path"]
_PROPERTY_NOT_FOUND_MESSAGE = "Property is missing:"


class DataWebdavAdapterTestCase(unittest.TestCase):
    """ Tests the data adapter implementation. """
    
    def setUp(self):
        """ Creates default adapter usable by test cases. """
        
        self._defaultAdapter = DataWebdavAdapter("/path/identifier", SimpleMock(), SimpleMock("identifier"), SimpleMock(SimpleMock()))
        
    def testLinkTarget(self):
        """ Tests the link target property. """
        
        adapter = DataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), SimpleMock({"/":(False, "/thelinkTargetPath")}))
        self.assertEquals(adapter.linkTarget, "/thelinkTargetPath")
        self.assertTrue(adapter.isLink)
        adapter = DataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), SimpleMock({"/":(False, None)}))
        self.assertEquals(adapter.linkTarget, None)
        self.assertFalse(adapter.isLink)

    def testIsLink(self):
        """ Tests the normal behavior of the isLink method. """
        
        adapter = DataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), SimpleMock({"/":(False, "/thelinkTargetPath")}))
        self.assertTrue(adapter.isLink)
        adapter = DataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), SimpleMock({"/":(False, None)}))
        self.assertFalse(adapter.isLink)

    def testIsLeaf(self):
        """ Tests the normal behavior of the isLeaf method. """
        
        adapter = DataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), SimpleMock({"/":(True, None)}))
        self.assertFalse(adapter.isLeaf)
        adapter = DataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), SimpleMock({"/":(False, "/thelinkTargetPath")}))
        self.assertFalse(adapter.isLeaf)
        adapter = DataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), SimpleMock({"/":(False, None)}))
        self.assertTrue(adapter.isLeaf)
        
    def testIsCollection(self):
        """ Tests the normal behavior of the isCollection method. """
        
        adapter = DataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), SimpleMock({"/":(True, None)}))
        self.assertTrue(adapter.isCollection)
        self.assertTrue(adapter.canAddChildren)
        adapter = DataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), SimpleMock({"/":(False, "/thelinkTargetPath")}))
        self.assertFalse(adapter.isCollection)
        self.assertFalse(adapter.canAddChildren)
        adapter = DataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), SimpleMock({"/":(False, None)}))
        self.assertFalse(adapter.isCollection)
        self.assertFalse(adapter.canAddChildren)
    
    def testCreateResource(self):
        """ Tests the normal behavior of the createResource method. """

        self._defaultAdapter.createResource()
        adapter = DataWebdavAdapter("identifier", SimpleMock(), SimpleMock(""), SimpleMock(SimpleMock()))
        self.assertRaises(PersistenceError, adapter.createResource)
        
    def testCreateLink(self):
        """ Tests the normal behavior of the createLink method. """

        self._defaultAdapter.createLink(self._defaultAdapter)
        
    def testCreateCollection(self):
        """ Tests the normal behavior of the createCollection method. """

        self._defaultAdapter.createCollection()
        self._defaultAdapter.createCollection(True)
        
        adapter = DataWebdavAdapter("identifier", SimpleMock(), SimpleMock(""), SimpleMock(SimpleMock()))
        self.assertRaises(PersistenceError, adapter.createCollection)
 
    def testGetChildren(self):
        """ Tests the normal behavior of the getChildren method. """

        adapter = DataWebdavAdapter("/identifier", SimpleMock(), SimpleMock("/Path"), 
                                    SimpleMock(_VALID_GETCHILDREN_WEBDAV_RESULT))
        self.assertEquals(adapter.getChildren(), _VALID_GETCHILDREN_RESULT)
        
    def testWriteData(self):
        """ Tests the normal behavior of the writeData method. """

        self._defaultAdapter.writeData(StringIO(""))
        
    def testReadData(self):
        """ Tests the normal behavior of the readData method. """

        adapter = DataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), SimpleMock(SimpleMock(StringIO(""))))
        self.assertTrue(isinstance(adapter.readData(), StringIO))
        
    def testDelete(self):
        """ Tests the normal behavior of the delete method. """
        
        self._defaultAdapter.delete()

    def testMove(self):
        """ Tests the normal behavior of the move method. """
        
        destination = DataWebdavAdapter("/anotherIdentifier", SimpleMock(), SimpleMock(), SimpleMock(SimpleMock()))
        self._defaultAdapter.move(destination)
    
    def testCopy(self):
        """ Tests the normal behavior of the copy method. """
        
        destination = DataWebdavAdapter("/anotherIdentifier", SimpleMock(), SimpleMock(), SimpleMock(SimpleMock()))
        self._defaultAdapter.copy(destination)
        
    def testExists(self):
        """ Tests the normal behavior of the exists method. """
        
        adapter = DataWebdavAdapter("/anotherIdentifier", SimpleMock(), SimpleMock(), SimpleMock(SimpleMock()))
        self.assertTrue(adapter.exists())
        adapter = DataWebdavAdapter("/anotherIdentifier", SimpleMock(), SimpleMock(), SimpleMock(error=WebdavError("", 404)))
        self.assertFalse(adapter.exists())
        adapter = DataWebdavAdapter("/anotherIdentifier", SimpleMock(), SimpleMock(), SimpleMock(error=WebdavError("")))
        self.assertRaises(PersistenceError, adapter.exists)

    def testErrorHandlingOnLibraryInstanceCreation(self):
        """ Tests the error handling when creating concrete library instances. """

        adapter = DataWebdavAdapter("/anotherIdentifier", SimpleMock(), SimpleMock("anotherIdentifier"), 
                                    SimpleMock(error=PersistenceError("")))
        try:
            self.assertFalse(adapter.isLink)
            self.fail("PersistenceError not raised.")
        except PersistenceError:
            self.assertTrue(True)
        try:
            self.assertFalse(adapter.isLeaf)
            self.fail("PersistenceError not raised.")
        except PersistenceError:
            self.assertTrue(True)
        try:
            self.assertFalse(adapter.isCollection)
            self.fail("PersistenceError not raised.")
        except PersistenceError:
            self.assertTrue(True)
        self.assertRaises(PersistenceError, adapter.createLink, self._defaultAdapter)
        self.assertRaises(PersistenceError, adapter.createResource)
        self.assertRaises(PersistenceError, adapter.createCollection)
        self.assertRaises(PersistenceError, adapter.getChildren)
        self.assertRaises(PersistenceError, adapter.writeData, StringIO(""))
        self.assertRaises(PersistenceError, adapter.readData)
        self.assertRaises(PersistenceError, adapter.delete)
        self.assertRaises(PersistenceError, adapter.move, self._defaultAdapter)
        self.assertRaises(PersistenceError, adapter.copy, self._defaultAdapter)

    def testErrorHandlingUsingLibraryInstances(self):
        """ Tests the error handling when using concrete library instances. """

        connectionHelperMock = SimpleMock(methodNameResultMap={"determineResourceType": (None, WebdavError(""))})
        adapter = DataWebdavAdapter("/anotherIdentifier", SimpleMock(), SimpleMock(""), connectionHelperMock)
        try:
            self.assertFalse(adapter.isLink)
            self.fail("PersistenceError not raised.")
        except PersistenceError:
            self.assertTrue(True)
        try:
            self.assertFalse(adapter.isLeaf)
            self.fail("PersistenceError not raised.")
        except PersistenceError:
            self.assertTrue(True)
        try:
            self.assertFalse(adapter.isCollection)
            self.fail("PersistenceError not raised.")
        except PersistenceError:
            self.assertTrue(True)
        self.assertRaises(PersistenceError, adapter.getChildren)
        
        connectionHelperMock = SimpleMock(SimpleMock(error=WebdavError("")))
        adapter = DataWebdavAdapter("/anotherIdentifier", SimpleMock(), SimpleMock(""), connectionHelperMock)
        self.assertRaises(PersistenceError, adapter.createLink, self._defaultAdapter)
        self.assertRaises(PersistenceError, adapter.createResource)
        self.assertRaises(PersistenceError, adapter.createCollection)
        self.assertRaises(PersistenceError, adapter.writeData, StringIO(""))
        self.assertRaises(PersistenceError, adapter.readData)
        self.assertRaises(PersistenceError, adapter.delete)
        self.assertRaises(PersistenceError, adapter.move, self._defaultAdapter)
        self.assertRaises(PersistenceError, adapter.copy, self._defaultAdapter)
