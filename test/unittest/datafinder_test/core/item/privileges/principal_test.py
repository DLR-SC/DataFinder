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
Tests the principal representation.
"""


from copy import deepcopy
import unittest

from datafinder.core.error import CoreError
from datafinder.core.item.privileges import principal
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


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
        
        self.assertEquals(self._principal, deepcopy(self._principal))
        
        self.assertTrue(self._principal in set([deepcopy(self._principal)]))
