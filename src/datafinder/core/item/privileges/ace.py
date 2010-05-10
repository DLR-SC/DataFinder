#
# Created: 29.01.2009 mohr_se <steven.mohr@dlr.de>
# Changed: $Id: ace.py 3858 2009-03-16 09:51:00Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


"""
Represents an entry of an access control list (ACL).
"""


from datafinder.core.error import PrivilegeError
from datafinder.core.principal import Principal
from datafinder.core.item.privileges.privilege import getPrivilege, ALL_PRIVILEGE, PRIVILEGES
from datafinder.persistence.privileges.ace import AccessControlListEntry as PersistenceAce


__version__ = "$LastChangedRevision: 3858 $"


class AccessControlListEntry(object):
    """
    Represents an entry of an access control list (ACL).
    """
    
    def __init__(self, principal, grantedPrivileges=None, deniedPrivileges=None):
        """
        @param principal: User / role the privileges are associated with.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        @param grantedPrivileges: Granted privileges
        @type grantedPrivileges: C{list} of L{privilege constants<datafinder.core.item.privileges.privilege>.
        @param deniedPrivileges: Denied privileges.
        @type deniedPrivileges: C{list} of L{privilege constants<datafinder.core.item.privileges.privilege>.
        """
        
        self.principal = principal
        
        if grantedPrivileges is None:
            self._grantedPrivileges = set()
        else:
            self._grantedPrivileges = set(grantedPrivileges)
        
        if deniedPrivileges is None:
            self._deniedPrivileges = set()
        else:
            self._deniedPrivileges = set(deniedPrivileges)
            
    def __getGrantedPrvileges(self):
        """ Getter for granted privileges. """
        
        return self._grantedPrivileges.copy()
            
    grantedPrivileges = property(__getGrantedPrvileges)
    
    def __getDeniedPrvileges(self):
        """ Getter for denied privileges. """
        
        return self._deniedPrivileges.copy()
    
    deniedPrivileges = property(__getDeniedPrvileges)
            
    def grantPrivilege(self, privilege):
        """
        Grants the given privilege.
        
        @param privilege: Privilege that is granted.
        @type privilege: L{privilege constants<datafinder.core.item.privileges.privilege>.
        """
        
        if privilege in PRIVILEGES:
            self._addPrivilege(privilege, True)
        else:
            raise PrivilegeError("The privilege %s is not supported." % repr(privilege))
    
    def denyPrivilege(self, privilege):
        """
        Denies the given privilege.
        
        @param privilege: Privilege that is denied.
        @type privilege: L{privilege constants<datafinder.core.item.privileges.privilege>.
        """
        
        if privilege in PRIVILEGES:
            self._addPrivilege(privilege, False)
        else:
            raise PrivilegeError("The privilege %s is not supported." % repr(privilege))
    
    def _addPrivilege(self, privilege, isGranted):
        """ Adds the privilege and resolves conflicting definitions. """
        
        if privilege == ALL_PRIVILEGE:
            self._grantedPrivileges.clear()
            self._deniedPrivileges.clear()
            if isGranted:
                self._grantedPrivileges.add(privilege)
            else:
                self._deniedPrivileges.add(privilege)
        else:
            if isGranted:
                self._grantedPrivileges.add(privilege)
                if privilege in self._deniedPrivileges:
                    self._deniedPrivileges.remove(privilege)
            else:
                self._deniedPrivileges.add(privilege)
                if privilege in self._grantedPrivileges:
                    self._grantedPrivileges.remove(privilege)

    def toPersistenceFormat(self):
        """
        Maps the access control list entry to the format required by the persistence layer.
        
        @return: Access control list entry in persistence format.
        @rtype: L{AccessControlListEntry<datafinder.persistence.privileges.ace.AccessControlListEntry>}
        """
        
        mappedGrantedPrivileges = list()
        for priv in self._grantedPrivileges:
            mappedGrantedPrivileges.append(priv.identifier)
        mappedDeniedPrivileges = list()
        for priv in self._deniedPrivileges:
            mappedDeniedPrivileges.append(priv.identifier)
        
        persistedAce = PersistenceAce()
        persistedAce.principal = self.principal.toPersistenceFormat()
        persistedAce.grantedPrivileges = mappedGrantedPrivileges
        persistedAce.deniedPrivileges = mappedDeniedPrivileges
        return persistedAce
    
    def __cmp__(self, other):
        """ Compares two instances. """
        
        if self.principal == other.principal \
           and self.grantedPrivileges == other.grantedPrivileges \
           and self.deniedPrivileges == other.deniedPrivileges:
            return 0
        return 1
    
    @staticmethod
    def create(ace):
        """ 
        Creates access control list entry from persistence format.
        
        @param ace: Access control list entry in persistence format.
        @type ace: L{AccessControlListEntry<datafinder.persistence.privileges.ace.AccessControlListEntry>}
        
        @raise PrivilegeError: In case of an unsupported privilege.
        """
        
        principal = Principal.create(ace.principal)
        grantedPrivileges = list()
        for privilegeId in ace.grantedPrivileges:
            grantedPrivileges.append(getPrivilege(privilegeId))
        deniedPrivileges = list()
        for privilegeId in ace.deniedPrivileges:
            deniedPrivileges.append(getPrivilege(privilegeId))
        return AccessControlListEntry(principal, grantedPrivileges, deniedPrivileges)
