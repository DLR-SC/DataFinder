#
# Created: 29.01.2009 mohr_se <steven.mohr@dlr.de>
# Changed: $Id: acl_test.py 3858 2009-03-16 09:51:00Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests the access control list representation.
"""


__version__ = "$LastChangedRevision: 3858 $"


import unittest

from datafinder.core.error import PrivilegeError
from datafinder.core.item.privileges import acl
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 3858 $"



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
