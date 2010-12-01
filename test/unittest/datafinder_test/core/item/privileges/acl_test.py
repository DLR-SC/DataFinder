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
Tests the access control list representation.
"""


__version__ = "$Revision-Id:$" 


import unittest

from datafinder.core.error import PrivilegeError
from datafinder.core.item.privileges import acl
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 



class _AceMock(object):
    """ Mocks the ace implementation. """
    
    mock = None
    principal = SimpleMock()
    
    def __init__(self, principal, grantedPrivileges=list(), deniedPrivileges=list()):
        """ Constructor. """
        
        self.principal = principal
        self.grantedPrivileges = set(grantedPrivileges)
        self.deniedPrivileges = set(deniedPrivileges)

    @staticmethod
    def create(anAce):
        """ Mocks the create implementation. """
    
        anAce.dummyCall() # Make a call to the mock to eventually raise an error
        return _AceMock(anAce)
    
    def __getattr__(self, name):
        """ Delegates to the internal mock representation. """
        
        return getattr(self.mock, name)
    
        
class AccessControlListTestCase(unittest.TestCase):
    """ 
    Tests for the ACL module. 
    """
    
    def setUp(self):
        """ Creates the required test environment. """

        self._aceMock = SimpleMock()
        _AceMock.mock = self._aceMock
        acl.AccessControlListEntry = _AceMock
        self._principalMock = SimpleMock()
        self._acl = acl.AccessControlList()
            
    def testPrincipalsAttribute(self):
        """ Tests the principals attribute. """
        
        self.assertEquals(self._acl.principals, list())
        self._acl.grantPrivilege(self._principalMock, "priv")
        self.assertEquals(self._acl.principals, [self._principalMock])
        
        principals = self._acl.principals
        principals.remove(self._principalMock)
        self.assertEquals(principals, list())
        self.assertEquals(self._acl.principals, [self._principalMock])
        
    def testGrantPrivilege(self):
        """ Tests granting of privileges. """
        
        self._acl.grantPrivilege(self._principalMock, "priv")
        self._acl.grantPrivilege(self._principalMock, "priv")
        self._acl.grantPrivilege(self._principalMock, "priv")
        self.assertEquals(self._acl.getGrantedPrivileges(self._principalMock), set(["priv"]))

        self._aceMock.error = PrivilegeError("")
        self.assertRaises(PrivilegeError, self._acl.grantPrivilege, self._principalMock, "unsupported-priv")

    def testDenyPrivilege(self):
        """ Tests denying of privileges. """
        
        self._acl.denyPrivilege(self._principalMock, "priv")
        self._acl.denyPrivilege(self._principalMock, "priv")
        self._acl.denyPrivilege(self._principalMock, "priv")
        self.assertEquals(self._acl.getDeniedPrivileges(self._principalMock), set(["priv"]))

        self._aceMock.error = PrivilegeError("")
        self.assertRaises(PrivilegeError, self._acl.denyPrivilege, self._principalMock, "unsupported-priv")
    
    def testToPersistenceFormat(self):
        """ Tests the mapping into the persistence format. """
        
        self._acl.grantPrivilege(self._principalMock, "priv1")
        
        self.assertEquals(self._acl.getGrantedPrivileges(self._principalMock), set(["priv1"]))
        self.assertEquals(len(self._acl.toPersistenceFormat()), 1)
        
        self._aceMock.error = PrivilegeError("")
        self.assertRaises(PrivilegeError, self._acl.toPersistenceFormat)

    def testCreate(self):
        """ Tests the creation of ACL. """
        
        newAcl = self._acl.create([SimpleMock(), SimpleMock(), SimpleMock()])
        self.assertEquals(len(newAcl.principals), 3)

        self.assertRaises(PrivilegeError, self._acl.create, [SimpleMock(error=PrivilegeError(""))])

    def testComparison(self):
        """ Tests the comparison of two instances. """
    
        self.assertEquals(self._acl, self._acl)
        
        anotherAcl = acl.AccessControlList()
        self.assertEquals(self._acl, anotherAcl)
        
        aPrincipal = SimpleMock()
        anotherAcl.grantPrivilege(aPrincipal, "priv")
        self.assertNotEquals(self._acl, anotherAcl)
        
        self._acl.grantPrivilege(aPrincipal, "priv")
        self.assertEquals(self._acl, anotherAcl)
