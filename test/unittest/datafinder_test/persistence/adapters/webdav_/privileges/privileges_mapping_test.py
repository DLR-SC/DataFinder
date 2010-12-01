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


__version__ = "$Revision-Id:$" 


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
