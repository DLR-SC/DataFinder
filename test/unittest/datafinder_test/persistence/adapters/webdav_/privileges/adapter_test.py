#
# Created: 23.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: adapter_test.py 3805 2009-02-23 13:00:19Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Test cases of the privilege adapter.
"""


__version__ = "$LastChangedRevision: 3805 $"


import unittest

from webdav.Connection import WebdavError

from datafinder.persistence.principal_search import principal
from datafinder.persistence.privileges.ace import AccessControlListEntry
from datafinder.persistence.adapters.webdav_.privileges.adapter import PrivilegeWebdavAdapter
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


_VALID_ACL = [AccessControlListEntry(principal.Principal("id"))]


class PrivilegeWebdavAdapterTestCase(unittest.TestCase):
    """ Test case of the privilege adapter. """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._privilegeMapperMock = SimpleMock()
        self._connectionHelperMock = SimpleMock(SimpleMock())
        self._adapter = PrivilegeWebdavAdapter("identifier", SimpleMock(), SimpleMock(), 
                                               self._privilegeMapperMock, self._connectionHelperMock)
    
    def testRetrieveAcl(self):
        """ Tests the retrieval of an ACL. """
        
        self._privilegeMapperMock.value = _VALID_ACL
        self.assertEquals(self._adapter.retrieveAcl(), _VALID_ACL)
        
    def testUpdateAcl(self):
        """ Tests the update of an ACL. """
        
        self._adapter.updateAcl(_VALID_ACL)

    def testRetrievePrivileges(self):
        """ Tests the retrieval of user privileges. """
        
        self._privilegeMapperMock.value = list()
        self.assertEquals(self._adapter.retrievePrivileges(), list())

    def testErrorHandling(self):
        """ Tests the error handling. """
        
        self._connectionHelperMock.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._adapter.retrieveAcl)
        self.assertRaises(PersistenceError, self._adapter.updateAcl, dict())
        self.assertRaises(PersistenceError, self._adapter.retrievePrivileges)
        
        self._connectionHelperMock.error = None
        self._connectionHelperMock.value = SimpleMock(error=WebdavError(""))
        self.assertRaises(PersistenceError, self._adapter.retrieveAcl)
        self.assertRaises(PersistenceError, self._adapter.updateAcl, dict())
        self.assertRaises(PersistenceError, self._adapter.retrievePrivileges)
        