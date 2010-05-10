#
# Created: 15.03.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: ace_test.py 3858 2009-03-16 09:51:00Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests an access control list entry.
"""


import unittest

from datafinder.core.error import PrivilegeError
from datafinder.core.item.privileges import ace
from datafinder.core.item.privileges import privilege
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 3858 $"


class _PrincipalMock(object):
    """ Mocks a principal. """
    
    @staticmethod
    def create(principal):
        """ Mocks creation. """
        
        return principal
    

class AccessControlListEntryTestCase(unittest.TestCase):
    """ Tests an access control list entry. """
    
    def setUp(self):
        """ Creates object under test. """
        
        ace.PersistenceAce = SimpleMock
        ace.Principal = _PrincipalMock
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
        persistenceAce.principal = "principal"
        persistenceAce.grantedPrivileges = [privilege.READ_PRIVILEGE.identifier]
        persistenceAce.deniedPrivileges = [privilege.WRITE_PRIVILEGE.identifier]
        mappedAce = self._ace.create(persistenceAce)
        
        self.assertEquals(mappedAce.principal, "principal")
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
