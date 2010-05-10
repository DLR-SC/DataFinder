#
# Created: 01.03.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: adapter_test.py 3827 2009-03-02 15:25:39Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Test cases of the meta data adapter.
"""


import unittest

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.metadata import constants
from datafinder.persistence.metadata.value_mapping import MetadataValue
from datafinder.persistence.adapters.filesystem.metadata import adapter
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 3827 $"


class _OsModuleMock(SimpleMock):
    """ Mocks the relevant functions of the os module. """
    
    def __init__(self, returnValue=None, error=None):
        """ Constructor. """
        
        self.returnValue = returnValue
        self.error = error
        SimpleMock.__init__(self, returnValue, error)
        
    @staticmethod
    def strerror(errorNumber):
        """ Explicitly mocking the error interpretation function. """
        
        return str(errorNumber)


class MetadataFileSystemAdapterTestCase(unittest.TestCase):
    """ Test cases of the meta data adapter. """

    def setUp(self):
        """ Creates the test setup. """

        # Mocks os module
        self._osStatResult = SimpleMock()
        self._osStatResult.st_ctime = 788999998.0
        self._osStatResult.st_mtime = 788999998.0
        self._osStatResult.st_size = 788999998.0
        self._osModuleMock = _OsModuleMock(self._osStatResult)
        adapter.os = self._osModuleMock
        
        # Mocks mimetypes module
        self._mimetypesModuleMock = SimpleMock((None, None))
        adapter.mimetypes = self._mimetypesModuleMock
        
        self._adapter = adapter.MetadataFileSystemAdapter("/identifier", SimpleMock("/identifier"))

    def _initValidRetrieveResult(self, mimeType):
        """ Creates the expected result. """
        
        mappedResult = dict()
        mappedResult[constants.CREATION_DATETIME] = MetadataValue(str(self._osStatResult.st_ctime))
        mappedResult[constants.MODIFICATION_DATETIME] = MetadataValue(str(self._osStatResult.st_mtime))
        mappedResult[constants.SIZE] = MetadataValue(str(self._osStatResult.st_size))
        mappedResult[constants.MIME_TYPE] = MetadataValue(mimeType)
        mappedResult[constants.OWNER] = MetadataValue("")
        return mappedResult
                                                                    
    def testRetrieve(self):
        """ Tests the retrieve behavior. """
        
        expectedResult = self._initValidRetrieveResult("")
        self.assertEquals(self._adapter.retrieve(), expectedResult)
        
        result = self._adapter.retrieve([constants.OWNER])
        self.assertTrue(len(result) == 1)
        self.assertTrue(constants.OWNER in result)
        
        result = self._adapter.retrieve([constants.OWNER, constants.CREATION_DATETIME])
        self.assertTrue(len(result) == 2)
        self.assertTrue(constants.OWNER in result)
        self.assertTrue(constants.CREATION_DATETIME in result)
        
        self.assertEquals(self._adapter.retrieve([]), expectedResult)
        self.assertEquals(self._adapter.retrieve(None), expectedResult)
        
        self._mimetypesModuleMock.value = ("application/pdf", None)
        expectedResult = self._initValidRetrieveResult("application/pdf")
        self.assertEquals(self._adapter.retrieve(), expectedResult)
        
        self._osModuleMock.error = OSError()
        self.assertRaises(PersistenceError, self._adapter.retrieve)
        
    def testUpdate(self):
        """ Tests the update behavior. """
        
        self._adapter.update(dict())

    def testDelete(self):
        """ Tests the delete behavior. """
        
        self._adapter.delete(list())
        
    def testSearch(self):
        """ Tests the search behavior. """
        
        self.assertEquals(self._adapter.search(list()), list())
        self.assertEquals(self._adapter.search([("prop1", "=", "test")]), list())
