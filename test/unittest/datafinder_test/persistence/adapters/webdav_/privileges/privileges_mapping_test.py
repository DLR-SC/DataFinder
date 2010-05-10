#
# Created: 28.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: privileges_mapping_test.py 3824 2009-03-01 13:56:03Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements test cases for the privileges mapping.
"""


import unittest

from webdav.Constants import TAG_READ, TAG_READ_ACL, TAG_WRITE, TAG_WRITE_ACL, TAG_ALL, TAG_WRITE_CONTENT
from webdav.acp import ACL, ACE, GrantDeny, Privilege

from datafinder.persistence.adapters.webdav_.privileges.privileges_mapping import PrivilegeMapper
from datafinder.persistence.principal_search.constants import ALL_PRINCIPAL
from datafinder.persistence.principal_search.principal import Principal
from datafinder.persistence.privileges.ace import AccessControlListEntry
from datafinder.persistence.privileges import constants


__version__ = "$LastChangedRevision: 3824 $"


_VALID_WEBDAV_ACL = ACL()
_VALID_WEBDAV_ACL.aces = [TAG_READ]

class PrivilegeMapperTestCase(unittest.TestCase):
    """ Implements test cases for the privilege mapping. """

    def setUp(self):
        """ Creates test setup. """
        
        self._validWebdavAcl = ACL()
        self._validInterfaceAcl = list()
        
        self._initWebdavAcl()
        self._initInterfaceAcl()
        self._privilegeMapper = PrivilegeMapper("http://etst.de/users/", "http://etst.de/groups/")
        
    def _initWebdavAcl(self):
        """ Builds an ACL of the WebDAV library. """
        
        aces = list()
        ace = ACE() # ace of user test
        ace.principal.principalURL = "http://etst.de/users/test"
        grantDeny = GrantDeny()
        grantDeny.grantDeny = 1
        grantDeny.privileges = [Privilege(TAG_READ), Privilege(TAG_WRITE)]
        ace.grantDenies.append(grantDeny)
        aces.append(ace)
        
        ace = ACE()
        ace.principal.principalURL = "http://etst.de/users/test"
        grantDeny = GrantDeny()
        grantDeny.grantDeny = 0
        grantDeny.privileges = [Privilege(TAG_WRITE_ACL)]
        ace.grantDenies.append(grantDeny)
        aces.append(ace)
        
        ace = ACE() # ace of user test2
        ace.principal.property = TAG_ALL
        grantDeny = GrantDeny()
        grantDeny.grantDeny = 1
        grantDeny.privileges = [Privilege(TAG_READ), Privilege(TAG_WRITE)]
        ace.grantDenies.append(grantDeny)
        aces.append(ace)
        self._validWebdavAcl.aces = aces

    def _initInterfaceAcl(self):
        """ Builds corresponding interface-specific ACL. """
        
        principal = Principal("test", displayName="test")
        ace = AccessControlListEntry(principal)
        ace.grantedPrivileges = [constants.READ_PRIVILEGE, constants.WRITE_PRIVILEGE]
        ace.deniedPrivileges = [constants.WRITE_PRIVILEGES_PRIVILEGE]
        self._validInterfaceAcl.append(ace)
        
        principal = Principal(ALL_PRINCIPAL)
        ace = AccessControlListEntry(principal)
        ace.grantedPrivileges = [constants.READ_PRIVILEGE, constants.WRITE_PRIVILEGE]
        self._validInterfaceAcl.append(ace)
        
    def testMapAcl(self):
        """ Demonstrates default behavior of the mapAcl method. """

        self.assertEquals(self._privilegeMapper.mapAcl(self._validInterfaceAcl), self._validWebdavAcl)
        self.assertEquals(self._privilegeMapper.mapAcl([]), self._validWebdavAcl)
        self.assertRaises(TypeError, self._privilegeMapper.mapAcl, None)
        
    def testMapPersistenceAcl(self):
        """ Demonstrates default behavior of the mapPersistenceAcl method. """

        self.assertTrue(self._areInterfaceAclsEqual(self._privilegeMapper.mapPersistenceAcl(self._validWebdavAcl), 
                                                    self._validInterfaceAcl))
        self.assertEquals(self._privilegeMapper.mapPersistenceAcl(ACL()), list())
        self.assertRaises(AttributeError, self._privilegeMapper.mapPersistenceAcl, None)
        
    @staticmethod
    def _areInterfaceAclsEqual(firstAcl, secondAcl):
        """ Checks whether two ACLs on interface level are equal. """
        
        equal = True
        for ace in firstAcl:
            if not ace in secondAcl:
                equal = False
                break
        return equal
    
    def testMapPeristencePrivileges(self):
        """ Demonstrates the mapping of persistence privileges. """
        
        self.assertEquals(self._privilegeMapper.mapPersistencePrivileges([Privilege(TAG_READ), Privilege(TAG_READ_ACL), 
                                                                         Privilege(TAG_WRITE), Privilege(TAG_WRITE_ACL), 
                                                                         Privilege(TAG_ALL)]),
                          [constants.READ_PRIVILEGE, constants.READ_PRIVILEGES_PRIVILEGE, constants.WRITE_PRIVILEGE,
                           constants.WRITE_PRIVILEGES_PRIVILEGE, constants.ALL_PRIVILEGE])
        self.assertEquals(self._privilegeMapper.mapPersistencePrivileges([Privilege(TAG_WRITE_CONTENT)]), list())
        self.assertRaises(AttributeError, self._privilegeMapper.mapPersistencePrivileges, [None])
