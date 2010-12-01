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
        