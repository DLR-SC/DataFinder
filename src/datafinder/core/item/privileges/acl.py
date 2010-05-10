#
# Created: 29.01.2009 mohr_se <steven.mohr@dlr.de>
# Changed: $Id: acl.py 3858 2009-03-16 09:51:00Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Represents an access control list (ACL) of an item.
"""


from datafinder.core.item.privileges.ace import AccessControlListEntry


__version__ = "$LastChangedRevision: 3858 $"


class AccessControlList(object):
    """
    Represents an access control list (ACL) of an item.
    """
    
    def __init__(self, aces=None):
        """
        Constructor.
        
        @param aces: Optional list of access control list entries.
        @type aces: C{list} of L{AccesControlListEntry<datafinder.core.item.privileges.ace.AccesControlListEntry>}
        """
        
        self._aces = dict()

        if not aces is None:
            for ace in aces:
                self._aces[ace.principal] = ace
        
    def __getPrincipals(self):
        """ Getter for the principals. """
        
        return self._aces.keys()[:]
    
    principals = property(__getPrincipals)
        
    def grantPrivilege(self, principal, privilege):
        """ 
        Grants a privilege to a user / role.
        
        @param principal: User / role the privilege is granted.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        @param privilege: Granted privilege.
        @type privilege: L{privilege constants<datafinder.core.item.privileges.privilege>.
        """
        
        if not principal in self._aces:
            self._aces[principal] = AccessControlListEntry(principal, [privilege])
        else:
            self._aces[principal].grantPrivilege(privilege)
            
    def denyPrivilege(self, principal, privilege):
        """ 
        Denies a privilege for a user / role.
        
        @param principal: User / role the privilege is granted.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        @param privilege: Denied privilege.
        @type privilege: L{privilege constants<datafinder.core.item.privileges.privilege>.
        """
        
        if not principal in self._aces:
            self._aces[principal] = AccessControlListEntry(principal, deniedPrivileges=[privilege])
        else:
            self._aces[principal].denyPrivilege(privilege)

    def getGrantedPrivileges(self, principal):
        """ 
        Returns the privileges granted to a user / role.
        
        @param principal: User / role.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        
        @return: Set of granted privileges.
        @rtype: C{set} of L{privilege constants<datafinder.core.item.privileges.privilege>.  
        """
        
        privileges = set()
        if principal in self._aces:
            privileges = self._aces[principal].grantedPrivileges
        return privileges
    
    def getDeniedPrivileges(self, principal):
        """ 
        Returns the privileges denied for a user / role.
        
        @param principal: User / role.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        
        @return: Set of denied privileges.
        @rtype: C{set} of L{privilege constants<datafinder.core.item.privileges.privilege>.  
        """

        privileges = set()
        if principal in self._aces:
            privileges = self._aces[principal].deniedPrivileges
        return privileges
 
    def toPersistenceFormat(self):
        """
        Maps the access control lists to the format required by the persistence layer.
        
        @return: Access control list in persistence format.
        @rtype: C{list} of L{AccessControlListEntry<datafinder.persistence.privileges.ace.AccessControlListEntry>}
        """
        
        mappedAcl = list()
        for ace in self._aces.values():
            mappedAcl.append(ace.toPersistenceFormat())
        return mappedAcl
    
    @staticmethod
    def create(aces):
        """ 
        Creates an access control list from persistence format. 
        
        @param aces: Access control list entries in persistence format.
        @type aces: C{list} of L{AccessControlListEntry<datafinder.persistence.privileges.ace.AccessControlListEntry>}
        
        @raise PrivilegeError: In case of an unsupported privilege.
        """
        
        mappedAces = list()
        for ace in aces:
            mappedAces.append(AccessControlListEntry.create(ace))
        return AccessControlList(mappedAces)

    def __cmp__(self, other):
        """ Compares two ACLs. """
        
        if len(self.principals) != len(other.principals):
            return 1
        for principal in self.principals:
            if self.getGrantedPrivileges(principal) != other.getGrantedPrivileges(principal) \
               or self.getDeniedPrivileges(principal) != other.getDeniedPrivileges(principal):
                return 1
        return 0
