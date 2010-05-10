#
# Created: 15.03.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: principal_test.py 3858 2009-03-16 09:51:00Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests the principal representation.
"""


import unittest

from datafinder.core.error import CoreError
from datafinder.core import principal
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 3858 $"


class PrincipalTestCase(unittest.TestCase):
    """ Tests the principal representation. """
    
    def setUp(self):
        """ Creates the object under test. """
        
        self._principal = principal.Principal("principal")
        groupPrincipal = principal.Principal("group")
        groupPrincipal.type = principal.GROUP_PRINCIPAL_TYPE
        self._principal.memberof.add(groupPrincipal)
    
    def testToPersistenceFormat(self):
        """ Tests the mapping into the principal format. """
        
        mappedPrincipal = self._principal.toPersistenceFormat()
        self.assertEquals(mappedPrincipal.identifier, "principal")
        self.assertEquals(mappedPrincipal.type, principal.USER_PRINCIPAL_TYPE.identifier)
        self.assertEquals(len(self._principal.memberof), 1)
        for member in mappedPrincipal.memberof:
            self.assertEquals(member.identifier, "group")
            self.assertEquals(member.type, principal.GROUP_PRINCIPAL_TYPE.identifier)
            
    def testCreate(self):
        """ Tests the creation from persistence format. """
        
        persistedPrincipal = SimpleMock()
        persistedPrincipal.identifier = "principal"
        persistedPrincipal.type = "____user____"
        persistedGroup = SimpleMock()
        persistedGroup.identifier = "group"
        persistedGroup.type = "____group____"
        persistedGroup.memberof = list()
        persistedPrincipal.memberof = [persistedGroup]
        mappedPrincipal = self._principal.create(persistedPrincipal)
        self.assertEquals(mappedPrincipal, self._principal)
        self.assertEquals(len(mappedPrincipal.memberof), 1)
        
        # Checking loop detection
        persistedPrincipal.memberof.append(persistedPrincipal)
        self.assertRaises(CoreError, self._principal.create, persistedPrincipal)
        
        # Checking invalid type
        persistedPrincipal.type = "unknown"
        self.assertRaises(CoreError, self._principal.create, persistedPrincipal)

    def testComparison(self):
        """ Tests the comparison of principal instances. """
        
        self.assertEquals(self._principal, self._principal)
        
        anotherPrincipal = principal.Principal("identifier")
        self.assertNotEquals(self._principal, anotherPrincipal)
        
        anotherPrincipal.identifier = self._principal.identifier
        self.assertEquals(self._principal, anotherPrincipal)
        
        anotherPrincipal.type = principal.GROUP_PRINCIPAL_TYPE
        self.assertNotEquals(self._principal, anotherPrincipal)
        