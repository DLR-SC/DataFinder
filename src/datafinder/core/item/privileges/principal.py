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
Represents an user / group / role.
"""


from datafinder.core.error import PrincipalError
from datafinder.persistence.principal_search.principal import constants, Principal as PersistedPrincipal


__version__ = "$Revision-Id:$" 


class _PrincipalType(object):
    """
    This class defines available properties of a principal type.
    The class mainly exists for documentation reasons and is intended
    to be replaced by named tuples when switching to Python 3.
    """
    
    def __init__(self, identifier, displayName, description):
        """
        Constructor.
        
        @param identifier: Identifier of the principal type.
        @type identifier: C{unicode}
        @param displayName: Display name of the principal type.
        @type displayName: C{unicode}
        @param description: Description of the principal type.
        @type description: C{unicode}
        """
        
        self.identifier = identifier
        self.displayName = displayName
        self.description = description


USER_PRINCIPAL_TYPE = _PrincipalType(constants.USER_PRINCIPAL_TYPE, "User Type", "Represents a user.")
GROUP_PRINCIPAL_TYPE = _PrincipalType(constants.GROUP_PRINCIPAL_TYPE, "Group Type", "Represents a group.")

PRINCIPAL_TYPES = [USER_PRINCIPAL_TYPE, GROUP_PRINCIPAL_TYPE]


class Principal(object):
    """
    Represents an user / group / role.
    """
    
    def __init__(self, identifier, displayName=None):
        """
        @param identifier: Identifier of the principal.
        @type identifier: C{unicode}
        @param displayName: Identifier of the principal.
        @type displayName: C{unicode}
        """
        
        self.identifier = identifier
        self.displayName = displayName 
        self.type = USER_PRINCIPAL_TYPE
        self.memberof = set()
        
        if displayName is None:
            self.displayName = self.identifier

    def __cmp__(self, other):
        """ Compares two instances. """
        
        if self.identifier == other.identifier \
           and self.type == other.type:
            return 0
        return 1
        
    def toPersistenceFormat(self):
        """
        Maps the principal to the format required by the persistence layer.
        
        @return: Principal in persistence format.
        @rtype: L{Principal<datafinder.persistence.principal_search.principal.Principal>}
        """
        
        mappedPrincipal = PersistedPrincipal(self.identifier)
        mappedPrincipal.type = self.type.identifier
        mappedPrincipal.displayName = self.displayName
        for principal in self.memberof:
            mappedPrincipal.memberof.append(principal.toPersistenceFormat())
        return mappedPrincipal
        
    @staticmethod
    def create(principal):
        """ 
        Creates a principal from the persistence representation.
        
        @return: User / group / role.
        @rtype: L{Principal<datafinder.persistence.principal_search.principal.Principal>}
        
        @raise CoreError: Indicates invalid principal type and infinite loops.
        """
        
        mappedPrincipal = Principal(principal.identifier)
        foundPrincipalType = False
        for principalType in PRINCIPAL_TYPES:
            if principalType.identifier == principal.type:
                mappedPrincipal.type = principalType
                foundPrincipalType = True
        if not foundPrincipalType:
            raise PrincipalError("Unsupported principal type '%s'." % principal.type)
        mappedPrincipal.displayName = principal.displayName
        try:
            for principal in principal.memberof:
                mappedPrincipal.memberof.add(Principal.create(principal))
        except RuntimeError:
            raise PrincipalError("Detected loop when trying to find out the groups the principal is member of.")
        return mappedPrincipal


OWNER_PRINCIPAL = Principal("____owner____", "Owner")
AUTHENTICATED_PRINCIPAL = Principal("____authenticated____", "Authenticated Principal")
AUTHENTICATED_PRINCIPAL.type = GROUP_PRINCIPAL_TYPE
UNAUTHENTICATED_PRINCIPAL = Principal("____unauthenticated____", "Unauthenticated Principal")
UNAUTHENTICATED_PRINCIPAL.type = GROUP_PRINCIPAL_TYPE

SPECIAL_PRINCIPALS = [OWNER_PRINCIPAL, AUTHENTICATED_PRINCIPAL, UNAUTHENTICATED_PRINCIPAL]
