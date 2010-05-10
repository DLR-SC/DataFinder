#
# Created: 29.01.2009 mohr_se <steven.mohr@dlr.de>
# Changed: $Id: principal.py 3858 2009-03-16 09:51:00Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Represents an user / group / role.
"""


from datafinder.core.error import CoreError
from datafinder.persistence.principal_search.principal import Principal as PersistedPrincipal


__version__ = "$LastChangedRevision: 3858 $"


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


USER_PRINCIPAL_TYPE = _PrincipalType("____user____", "User Type", "Represents a user.")
GROUP_PRINCIPAL_TYPE = _PrincipalType("____group____", "Group Type", "Represents a group.")

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
            raise CoreError("Unsupported principal type '%s'." % principal.type)
        mappedPrincipal.displayName = principal.displayName
        try:
            for principal in principal.memberof:
                mappedPrincipal.memberof.add(Principal.create(principal))
        except RuntimeError:
            raise CoreError("Detected loop when trying to find out the groups the principal is member of.")
        return mappedPrincipal


OWNER_PRINCIPAL = Principal("____owner____", "Owner")
AUTHENTICATED_PRINCIPAL = Principal("____authenticated____", "Authenticated Principal")
UNAUTHENTICATED_PRINCIPAL = Principal("____unauthenticated____", "Unauthenticated Principal")

SPECIAL_PRINCIPALS = [OWNER_PRINCIPAL, AUTHENTICATED_PRINCIPAL, UNAUTHENTICATED_PRINCIPAL]
