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
Test cases of the principal search adapter.
"""


import unittest

from webdav.Connection import WebdavError
from webdav.Constants import NS_DAV, PROP_DISPLAY_NAME

from datafinder.persistence.principal_search import constants, principal
from datafinder.persistence.adapters.webdav_.principal_search.adapter import PrincipalSearchWebdavAdapter
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 3805 $"


_VALID_WEBDAV_USER_RESULT = {"http://test.de/path/user1": {(NS_DAV, PROP_DISPLAY_NAME):SimpleMock("displayName")}}
_VALID_USER_RESULT = [principal.Principal("user1", displayName="displayName")]

_VALID_WEBDAV_GROUP_RESULT = {"http://test.de/path/group1": {(NS_DAV, PROP_DISPLAY_NAME):SimpleMock("displayName")}}
_VALID_GROUP_RESULT = [principal.Principal("group1", type=constants.GROUP_PRINCIPAL_TYPE, displayName="displayName")]
_VALID_USER_GROUP_RESULT = [_VALID_USER_RESULT[0], _VALID_GROUP_RESULT[0]]


class _WebDAVSearchMethodMock(object):
    """ Mock of the search method. """
    
    def __init__(self):
        """ Constructor. """
        self.counter = 0
        
    def search(self, _, __):
        """ Search method mock. """
        
        if self.counter == 0:
            self.counter += 1
            return _VALID_WEBDAV_GROUP_RESULT
        else:
            self.counter = 0
            return _VALID_WEBDAV_USER_RESULT 
        

class PrincipalSearchWebdavAdapterTestCase(unittest.TestCase):
    """ Test cases of the principal search adapter. """

    def testPrincipalSearch(self):
        """ Tests the default behavior of the principal search. """
        
        adapter = PrincipalSearchWebdavAdapter("userCollectionUrl", "groupCollectionUrl", SimpleMock(), 
                                               SimpleMock(_WebDAVSearchMethodMock()))
        self.assertEquals(adapter.searchPrincipal("pattern", constants.SEARCH_MODE_GROUP_ONLY), _VALID_GROUP_RESULT)
        self.assertEquals(adapter.searchPrincipal("pattern", constants.SEARCH_MODE_USER_ONLY), _VALID_USER_RESULT)
        self.assertEquals(adapter.searchPrincipal("pattern", constants.SEARCH_MODE_USER_AND_GROUP), _VALID_USER_GROUP_RESULT)
        
    def testErrorHandling(self):
        """ Tests the default behavior of the principal search. """
        
        adapter = PrincipalSearchWebdavAdapter("userCollectionUrl", "groupCollectionUrl", SimpleMock(), 
                                               SimpleMock(error=PersistenceError("")))
        self.assertRaises(PersistenceError, adapter.searchPrincipal, "pattern", constants.SEARCH_MODE_GROUP_ONLY)
        
        adapter = PrincipalSearchWebdavAdapter("userCollectionUrl", "groupCollectionUrl", SimpleMock(), 
                                               SimpleMock(SimpleMock(error=WebdavError(""))))
        self.assertRaises(PersistenceError, adapter.searchPrincipal, "pattern", constants.SEARCH_MODE_GROUP_ONLY)
        
        adapter = PrincipalSearchWebdavAdapter("userCollectionUrl", "groupCollectionUrl", SimpleMock(), SimpleMock())
        self.assertRaises(PersistenceError, adapter.searchPrincipal, "pattern", "unknownSearchMode")
