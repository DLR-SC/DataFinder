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
Test cases of the principal search adapter.
"""


import unittest

from webdav.Connection import WebdavError
from webdav.Constants import NS_DAV, PROP_DISPLAY_NAME

from datafinder.persistence.principal_search import constants, principal
from datafinder.persistence.adapters.webdav_.principal_search.adapter import PrincipalSearchWebdavAdapter
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


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
