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


from copy import deepcopy
import unittest

from datafinder.core.error import PrivilegeError, PrincipalError
from datafinder.core.item.privileges import acl, privilege
from datafinder.core.item.privileges.privilege import NONE_ACCESS_LEVEL, \
                                                      READ_ONLY_ACCESS_LEVEL, FULL_ACCESS_LEVEL
from datafinder.persistence.principal_search import principal
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 



class _PersistenceAceMock(object):
    """ Mocks the persistence ACE. """
    
    def __init__(self, principalId):
        """ Constructor. """
        
        self.principal = principal.Principal(principalId)
        self.grantedPrivileges = list()
        self.deniedPrivileges = list()
    
    
class AccessControlListTestCase(unittest.TestCase):
    """ 
    Tests for the ACL module. 
    """


    _SUPPORTED_PRIVILEGE = privilege.READ_PRIVILEGE
    _UNSUPPORTED_PRIVILEGE = SimpleMock(identifier="UNSUPPORTED")    
    
    
    def setUp(self):
        """ Creates the required test environment. """

        self._principalMock = SimpleMock(identifier="id")
        self._acl = acl.AccessControlList()
            
    def testPrincipalsAttribute(self):
        """ Tests the principals attribute. """
        
        self.assertEquals(self._acl.principals, list())
        self._acl.grantPrivilege(self._principalMock, self._SUPPORTED_PRIVILEGE)
        self.assertEquals(self._acl.principals, [self._principalMock])
        
        principals = self._acl.principals
        principals.remove(self._principalMock)
        self.assertEquals(principals, list())
        self.assertEquals(self._acl.principals, [self._principalMock])
        
    def testGrantPrivilege(self):
        """ Tests granting of privileges. """
        
        self._acl.grantPrivilege(self._principalMock, self._SUPPORTED_PRIVILEGE)
        self._acl.grantPrivilege(self._principalMock, self._SUPPORTED_PRIVILEGE)
        self._acl.grantPrivilege(self._principalMock, self._SUPPORTED_PRIVILEGE)
        self.assertEquals(self._acl.getGrantedPrivileges(self._principalMock), set([self._SUPPORTED_PRIVILEGE]))

        self.assertRaises(PrivilegeError, self._acl.grantPrivilege, self._principalMock, self._UNSUPPORTED_PRIVILEGE)

    def testDenyPrivilege(self):
        """ Tests denying of privileges. """
        
        self._acl.denyPrivilege(self._principalMock, self._SUPPORTED_PRIVILEGE)
        self._acl.denyPrivilege(self._principalMock, self._SUPPORTED_PRIVILEGE)
        self._acl.denyPrivilege(self._principalMock, self._SUPPORTED_PRIVILEGE)
        self.assertEquals(self._acl.getDeniedPrivileges(self._principalMock), set([self._SUPPORTED_PRIVILEGE]))

        self.assertRaises(PrivilegeError, self._acl.denyPrivilege, self._principalMock, self._UNSUPPORTED_PRIVILEGE)
    
    def testToPersistenceFormat(self):
        """ Tests the mapping into the persistence format. """
        
        self._acl.grantPrivilege(self._principalMock, self._SUPPORTED_PRIVILEGE)
        
        self.assertEquals(self._acl.getGrantedPrivileges(self._principalMock), 
                          set([self._SUPPORTED_PRIVILEGE]))
        self.assertEquals(len(self._acl.toPersistenceFormat()), 1)
        

    def testCreate(self):
        """ Tests the creation of ACL. """
        
        newAcl = self._acl.create([_PersistenceAceMock("a"), 
                                   _PersistenceAceMock("b"),
                                   _PersistenceAceMock("c")])
        self.assertEquals(len(newAcl.principals), 3)

        invalidPrivAce = _PersistenceAceMock("a")
        invalidPrivAce.grantedPrivileges = [self._UNSUPPORTED_PRIVILEGE]
        self.assertRaises(PrivilegeError, self._acl.create, [invalidPrivAce])

        invalidPrincipalAce = _PersistenceAceMock("a")
        invalidPrincipalAce.principal = SimpleMock("a")
        self.assertRaises(PrincipalError, self._acl.create, [invalidPrincipalAce])

    def testComparison(self):
        """ Tests the comparison of two instances. """
    
        self.assertEquals(self._acl, self._acl)
        
        anotherAcl = acl.AccessControlList()
        self.assertEquals(self._acl, anotherAcl)
        
        aPrincipal = SimpleMock(identifier="aPrincipal")
        anotherAcl.grantPrivilege(aPrincipal, self._SUPPORTED_PRIVILEGE)
        self.assertNotEquals(self._acl, anotherAcl)
        
        self._acl.grantPrivilege(aPrincipal, self._SUPPORTED_PRIVILEGE)
        self.assertEquals(self._acl, anotherAcl)
        
        self.assertEquals(self._acl, deepcopy(self._acl))

    def testContentAccessLevel(self):
        """ Checks content access level handling. """
        
        self._acl.setContentAccessLevel(self._principalMock, NONE_ACCESS_LEVEL)
        self.assertEquals(self._acl.contentAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        self.assertEquals(self._acl.propertiestAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        self.assertEquals(self._acl.aministrationAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        
        self._acl.setContentAccessLevel(self._principalMock, READ_ONLY_ACCESS_LEVEL)
        self.assertEquals(self._acl.contentAccessLevel(self._principalMock),
                          READ_ONLY_ACCESS_LEVEL)
        self.assertEquals(self._acl.propertiestAccessLevel(self._principalMock),
                          READ_ONLY_ACCESS_LEVEL)
        self.assertEquals(self._acl.aministrationAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        
        self._acl.setContentAccessLevel(self._principalMock, FULL_ACCESS_LEVEL)
        self.assertEquals(self._acl.contentAccessLevel(self._principalMock),
                          FULL_ACCESS_LEVEL)
        self.assertEquals(self._acl.propertiestAccessLevel(self._principalMock),
                          READ_ONLY_ACCESS_LEVEL)
        self.assertEquals(self._acl.aministrationAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        
    def testPropertiesAccessLevel(self):
        """ Checks properties access level handling. """
        
        self._acl.setPropertiesAccessLevel(self._principalMock, NONE_ACCESS_LEVEL)
        self.assertEquals(self._acl.contentAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        self.assertEquals(self._acl.propertiestAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        self.assertEquals(self._acl.aministrationAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        
        self._acl.setPropertiesAccessLevel(self._principalMock, READ_ONLY_ACCESS_LEVEL)
        self.assertEquals(self._acl.contentAccessLevel(self._principalMock),
                          READ_ONLY_ACCESS_LEVEL)
        self.assertEquals(self._acl.propertiestAccessLevel(self._principalMock),
                          READ_ONLY_ACCESS_LEVEL)
        self.assertEquals(self._acl.aministrationAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        
        self._acl.setPropertiesAccessLevel(self._principalMock, FULL_ACCESS_LEVEL)
        self.assertEquals(self._acl.contentAccessLevel(self._principalMock),
                          READ_ONLY_ACCESS_LEVEL)
        self.assertEquals(self._acl.propertiestAccessLevel(self._principalMock),
                          FULL_ACCESS_LEVEL)
        self.assertEquals(self._acl.aministrationAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        
    def testAdministrationAccessLevel(self):
        """ Checks administration access level handling. """
        
        self._acl.setAministrationAccessLevel(self._principalMock, NONE_ACCESS_LEVEL)
        self.assertEquals(self._acl.contentAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        self.assertEquals(self._acl.propertiestAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        self.assertEquals(self._acl.aministrationAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        
        self._acl.setAministrationAccessLevel(self._principalMock, READ_ONLY_ACCESS_LEVEL)
        self.assertEquals(self._acl.contentAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        self.assertEquals(self._acl.propertiestAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        self.assertEquals(self._acl.aministrationAccessLevel(self._principalMock),
                          READ_ONLY_ACCESS_LEVEL)
        
        self._acl.setAministrationAccessLevel(self._principalMock, FULL_ACCESS_LEVEL)
        self.assertEquals(self._acl.contentAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        self.assertEquals(self._acl.propertiestAccessLevel(self._principalMock),
                          NONE_ACCESS_LEVEL)
        self.assertEquals(self._acl.aministrationAccessLevel(self._principalMock),
                          FULL_ACCESS_LEVEL)

    def testClearPrivileges(self):
        """ Tests clearing of privileges. """
        
        self._acl.setAministrationAccessLevel(self._principalMock, NONE_ACCESS_LEVEL)
        self.assertEquals(len(self._acl.principals), 1)
        
        self._acl.clearPrivileges(self._principalMock)
        self.assertEquals(len(self._acl.principals), 0)

    def testIndex(self):
        """ Tests the index handling. """
        
        # Initially adding two principals
        self._acl.setContentAccessLevel(self._principalMock, FULL_ACCESS_LEVEL)
        self.assertEquals(self._acl.getIndex(self._principalMock), 0)
        anotherPrincipal = SimpleMock(identifier="anotherPrincipal")
        self._acl.setContentAccessLevel(anotherPrincipal, FULL_ACCESS_LEVEL)
        self.assertEquals(self._acl.getIndex(anotherPrincipal), 1)

        # Playing with the indexes        
        self._acl.setIndex(self._principalMock, 1)
        self.assertEquals(self._acl.getIndex(anotherPrincipal), 0)
        self.assertEquals(self._acl.getIndex(self._principalMock), 1)
        self._acl.setIndex(anotherPrincipal, 3) # The index does not exists
        self.assertEquals(self._acl.getIndex(anotherPrincipal), 1)
        self.assertEquals(self._acl.getIndex(self._principalMock), 0)
        
        # Clearing everything and testing error handling
        self._acl.clearPrivileges(self._principalMock)
        self._acl.clearPrivileges(anotherPrincipal)
        self.assertRaises(ValueError, self._acl.getIndex, self._principalMock)

    def testAddDefaultPrincipal(self):
        """ Tests the default principal adding method. """
        
        self._acl.addDefaultPrincipal(self._principalMock)
        self.assertEquals(self._acl.contentAccessLevel(self._principalMock), READ_ONLY_ACCESS_LEVEL)
        self.assertEquals(self._acl.propertiestAccessLevel(self._principalMock), READ_ONLY_ACCESS_LEVEL)
        self.assertEquals(self._acl.aministrationAccessLevel(self._principalMock), NONE_ACCESS_LEVEL)
