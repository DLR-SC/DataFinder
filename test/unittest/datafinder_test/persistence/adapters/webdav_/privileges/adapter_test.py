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
Test cases of the privilege adapter.
"""


__version__ = "$Revision-Id:$" 


import unittest

from webdav.Connection import WebdavError

from datafinder.persistence.principal_search import principal
from datafinder.persistence.privileges import constants
from datafinder.persistence.privileges.ace import AccessControlListEntry
from datafinder.persistence.adapters.webdav_.privileges import adapter
from datafinder.persistence.adapters.webdav_.privileges import privileges_mapping
from datafinder.persistence.error import PersistenceError
from datafinder_test.mocks import SimpleMock


_VALID_ACL = [AccessControlListEntry(principal.Principal("id"))]


class PrivilegeWebdavAdapterTestCase(unittest.TestCase):
    
    def setUp(self):
        self._privilegeMapper = SimpleMock()
        self._connectionHelper = SimpleMock(SimpleMock())
        self._adapter = adapter.PrivilegeWebdavAdapter(
            "identifier", SimpleMock(), SimpleMock(), self._privilegeMapper, self._connectionHelper)
    
    def testRetrieveAcl(self):
        self._privilegeMapper.value = _VALID_ACL
        self.assertEquals(self._adapter.retrieveAcl(), _VALID_ACL)
        
    def testUpdateAcl(self):
        self._privilegeMapper.value = _VALID_ACL
        self._adapter.updateAcl(_VALID_ACL)

    def testRetrievePrivileges(self):
        self._privilegeMapper.value = list()
        self.assertEquals(self._adapter.retrievePrivileges(), list())

    def testErrorHandling(self):
        self._connectionHelper.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._adapter.retrieveAcl)
        self.assertRaises(PersistenceError, self._adapter.updateAcl, dict())
        self.assertRaises(PersistenceError, self._adapter.retrievePrivileges)
        
        self._connectionHelper.error = None
        self._connectionHelper.value = SimpleMock(error=WebdavError(""))
        self.assertRaises(PersistenceError, self._adapter.retrieveAcl)
        self.assertRaises(PersistenceError, self._adapter.updateAcl, dict())
        self.assertRaises(PersistenceError, self._adapter.retrievePrivileges)
        
class SimplePrivilegeWebdavAdapterTestCase(unittest.TestCase):
    
    def setUp(self):
        self._privilegeMapper = privileges_mapping.PrivilegeMapper("", "")
        self._connectionHelper = SimpleMock(SimpleMock())
        self._adapter = adapter.SimplePrivilegeWebdavAdapter(
            "identifier", SimpleMock(), SimpleMock(), self._privilegeMapper, self._connectionHelper)
        
    def testRetrievePrivilegesSuccess(self):
        self._connectionHelper.value.value = {
            "allow": ["GET", "PROPFIND", "PROPPATCH", "POST", "DELETE", "COPY", "MOVE"]}
        self.assertEquals(
            self._adapter.retrievePrivileges(), 
            [constants.READ_PRIVILEGE, constants.WRITE_CONTENT_PRIVILEGE, constants.WRITE_PROPERTIES_PRIVILEGE])
        
    def testRetrievePrivilegesEmptyAllow(self):
        self._connectionHelper.value.value = dict()
        self.assertEquals(self._adapter.retrievePrivileges(), list())
        
    def testRetrievePrivilegesError(self):
        self._connectionHelper.error = PersistenceError("")
        self.assertRaises(PersistenceError, self._adapter.retrievePrivileges)
