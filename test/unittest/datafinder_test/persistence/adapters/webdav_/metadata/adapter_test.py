#
# Created: 21.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: adapter_test.py 3865 2009-03-19 09:26:12Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests the meta data adapter implementation.
"""


import unittest

from webdav.Connection import WebdavError

from datafinder.persistence.adapters.webdav_.metadata.adapter import MetadataWebdavAdapter
from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata import constants
from datafinder.persistence.metadata.value_mapping import MetadataValue
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 3865 $"


_VALID_WEBDAV_PROPERTY_RESULT = {("1", "1"): SimpleMock("")}
_VALID_PROPERTY_RESULT = {constants.CREATION_DATETIME: MetadataValue(""), 
                          constants.MODIFICATION_DATETIME: MetadataValue(""),
                          constants.SIZE: MetadataValue("0"), 
                          constants.MIME_TYPE: MetadataValue(""), 
                          constants.OWNER: MetadataValue("")}

_VALID_WEBDAV_SEARCH_RESULT = {"http://server.de/Path": SimpleMock()}
_VALID_SEARCH_RESULT = ["/PATH"]


class MetadataWebdavAdapterTestCase(unittest.TestCase):
    """ Tests the meta data adapter implementation. """

    def setUp(self):
        """ Creates a default object under test. """
        
        self._defaultAdapter = MetadataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), 
                                                     SimpleMock(), SimpleMock(SimpleMock()))

    def testRetrieveSuccess(self):
        """ Tests successful meta data retrieval. """
        
        webdavStorerMock = SimpleMock(dict())
        adapter = MetadataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), 
                                        SimpleMock("1"), SimpleMock(webdavStorerMock))
        self.assertEquals(adapter.retrieve(), _VALID_PROPERTY_RESULT)
        self.assertEquals(adapter.retrieve(list()), dict())
        
        webdavStorerMock.value = {("1", "1"): SimpleMock("value")}
        self.assertEquals(adapter.retrieve(["1"]), {"1": MetadataValue("value")})

    def testUpdateSuccess(self):
        """ Tests successful update of meta data. """
        
        self._defaultAdapter.update({"1":"", "2":"", "3":""})
    
    def testDeleteSuccess(self):
        """ Tests successful deletion of meta data. """
        
        self._defaultAdapter.delete(["1", "2"])
    
    def testSearchSuccess(self):
        """ Tests successful deletion of meta data. """
        
        adapter = MetadataWebdavAdapter("identifier", SimpleMock(), SimpleMock("/PATH"), 
                                        SimpleMock(), SimpleMock(SimpleMock(_VALID_WEBDAV_SEARCH_RESULT)))
        self.assertEquals(adapter.search([]), _VALID_SEARCH_RESULT)

    def testErrorHandlingOnLibraryInstanceCreation(self):
        """ Tests the error handling when creating concrete library instances. """

        adapter = MetadataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), 
                                        SimpleMock(), SimpleMock(error=PersistenceError("")))
        self.assertRaises(PersistenceError, adapter.retrieve)
        self.assertRaises(PersistenceError, adapter.update, dict())
        self.assertRaises(PersistenceError, adapter.delete, [])
        self.assertRaises(PersistenceError, adapter.search, [])

    def testErrorHandlingUsingLibraryInstances(self):
        """ Tests the error handling when using concrete library instances. """

        adapter = MetadataWebdavAdapter("identifier", SimpleMock(), SimpleMock(), 
                                        SimpleMock(), SimpleMock(SimpleMock(error=WebdavError(""))))
        self.assertRaises(PersistenceError, adapter.retrieve)
        self.assertRaises(PersistenceError, adapter.update, dict())
        self.assertRaises(PersistenceError, adapter.delete, [])
        self.assertRaises(PersistenceError, adapter.search, [])
