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
Tests an access control list entry.
"""


import unittest

from datafinder.core.error import PrivilegeError
from datafinder.core.item.privileges import ace
from datafinder.core.item.privileges import privilege
from datafinder.persistence.principal_search import principal
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class AccessControlListEntryTestCase(unittest.TestCase):
    """ Tests an access control list entry. """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._ace = ace.AccessControlListEntry(SimpleMock("principal"))
    
    def testGrantPrivilege(self):
        """ Tests the privilege granting. """
        
        self._ace.grantPrivilege(privilege.READ_PRIVILEGE)
        self.assertEquals(self._ace.grantedPrivileges, set([privilege.READ_PRIVILEGE]))
        
        self.assertRaises(PrivilegeError, self._ace.grantPrivilege, "unknown_priv")
        
    def testDenyPrivilege(self):
        """ Tests the privilege denying. """
        
        self._ace.denyPrivilege(privilege.READ_PRIVILEGE)
        self.assertEquals(self._ace.deniedPrivileges, set([privilege.READ_PRIVILEGE]))
        
        self.assertRaises(PrivilegeError, self._ace.denyPrivilege, "unknown_priv")
        
    def testPrivilegeNormalizing(self):
        """ Shows the management of privileges. """

        self._ace.grantPrivilege(privilege.READ_PRIVILEGE)
        self._ace.grantPrivilege(privilege.WRITE_PRIVILEGE)
        self._ace.denyPrivilege(privilege.WRITE_PRIVILEGE)
        self.assertEquals(self._ace.grantedPrivileges, set([privilege.READ_PRIVILEGE]))
        self.assertEquals(self._ace.deniedPrivileges, set([privilege.WRITE_PRIVILEGE]))
        
        self._ace.grantPrivilege(privilege.WRITE_PRIVILEGE)
        self.assertEquals(self._ace.grantedPrivileges, set([privilege.READ_PRIVILEGE, privilege.WRITE_PRIVILEGE]))
        self.assertEquals(self._ace.deniedPrivileges, set())
        
        self._ace.denyPrivilege(privilege.ALL_PRIVILEGE)
        self.assertEquals(self._ace.grantedPrivileges, set())
        self.assertEquals(self._ace.deniedPrivileges, set([privilege.ALL_PRIVILEGE]))
        
        self._ace.grantPrivilege(privilege.ALL_PRIVILEGE)
        self.assertEquals(self._ace.grantedPrivileges, set([privilege.ALL_PRIVILEGE]))
        self.assertEquals(self._ace.deniedPrivileges, set())
        
        self._ace.grantPrivilege(privilege.WRITE_PRIVILEGE)
        self.assertEquals(self._ace.grantedPrivileges, set([privilege.ALL_PRIVILEGE]))
        self.assertEquals(self._ace.deniedPrivileges, set())
        
        self._ace.denyPrivilege(privilege.WRITE_PRIVILEGE)
        self.assertEquals(self._ace.grantedPrivileges, set([privilege.ALL_PRIVILEGE]))
        self.assertEquals(self._ace.deniedPrivileges, set([privilege.WRITE_PRIVILEGE]))
        
        self._ace.denyPrivilege(privilege.ALL_PRIVILEGE)
        self.assertEquals(self._ace.grantedPrivileges, set([]))
        self.assertEquals(self._ace.deniedPrivileges, set([privilege.ALL_PRIVILEGE]))

    def testToPersistenceFormat(self):
        """ Tests the mapping to the persistence format. """
        
        self._ace.grantPrivilege(privilege.READ_PRIVILEGE)
        self._ace.denyPrivilege(privilege.WRITE_PRIVILEGE)
        
        mappedAce = self._ace.toPersistenceFormat()
        self.assertEquals(mappedAce.principal, "principal")
        self.assertEquals(mappedAce.grantedPrivileges, [privilege.READ_PRIVILEGE.identifier])
        self.assertEquals(mappedAce.deniedPrivileges, [privilege.WRITE_PRIVILEGE.identifier])

    def testCreate(self):
        """ Tests the creation of an ACE. """
        
        persistenceAce = SimpleMock()
        persistenceAce.principal = principal.Principal(identifier="principal")
        persistenceAce.grantedPrivileges = [privilege.READ_PRIVILEGE.identifier]
        persistenceAce.deniedPrivileges = [privilege.WRITE_PRIVILEGE.identifier]
        mappedAce = self._ace.create(persistenceAce)
        
        self.assertEquals(mappedAce.principal.identifier, "principal")
        self.assertEquals(mappedAce.grantedPrivileges, set([privilege.READ_PRIVILEGE]))
        self.assertEquals(mappedAce.deniedPrivileges, set([privilege.WRITE_PRIVILEGE]))

    def testComparison(self):
        """ Tests the comparison of two instances. """
        
        self.assertEquals(self._ace, self._ace)
        
        anotherAce = ace.AccessControlListEntry(SimpleMock("principal"))
        self.assertNotEquals(self._ace, anotherAce)
        
        anotherAce.principal = self._ace.principal
        self.assertEquals(self._ace, anotherAce)
        
        anotherAce.grantPrivilege(privilege.READ_PRIVILEGE)
        self.assertNotEquals(self._ace, anotherAce)
        
        self._ace.grantPrivilege(privilege.READ_PRIVILEGE)
        self.assertEquals(self._ace, anotherAce)
