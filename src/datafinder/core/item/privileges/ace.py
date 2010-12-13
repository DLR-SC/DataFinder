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
Represents an entry of an access control list (ACL).
"""


from datafinder.core.error import PrivilegeError
from datafinder.core.item.privileges.principal import Principal
from datafinder.core.item.privileges.privilege import getPrivilege, PRIVILEGES
from datafinder.persistence.privileges.ace import AccessControlListEntry as PersistenceAce


__version__ = "$Revision-Id:$" 


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
        @type privilege: L{privilege constants<datafinder.core.item.privileges.privilege>}
        """
        
        if privilege in PRIVILEGES:
            self._addPrivilege(privilege, self._grantedPrivileges, self._deniedPrivileges)
        else:
            raise PrivilegeError("The privilege %s is not supported." % repr(privilege))
    
    def denyPrivilege(self, privilege):
        """
        Denies the given privilege.
        
        @param privilege: Privilege that is denied.
        @type privilege: L{privilege constants<datafinder.core.item.privileges.privilege>}
        """
        
        if privilege in PRIVILEGES:
            self._addPrivilege(privilege, self._deniedPrivileges, self._grantedPrivileges)
        else:
            raise PrivilegeError("The privilege %s is not supported." % repr(privilege))
    
    @staticmethod
    def _addPrivilege(privilege, addTo, removeFrom):
        """ Adds the privilege and resolves conflicting definitions. """
        
        # check whether the privilege is already included in an existing
        privilegeAlreadyIncluded = False
        for privilege_ in addTo:
            if privilege in privilege_.aggregatedPrivileges:
                privilegeAlreadyIncluded = True
                break
        
        # Set the privilege and remove the aggregated
        if not privilegeAlreadyIncluded:
            aggregatedPrivileges = list()
            for privilege_ in privilege.aggregatedPrivileges:
                if privilege_ in addTo:
                    aggregatedPrivileges.append(privilege_)
            for privilege_ in aggregatedPrivileges:
                addTo.remove(privilege_)
            addTo.add(privilege)
        
        # Remove the privilege and all its "sub privileges" from the opposite
        for privilege_ in [privilege] + privilege.aggregatedPrivileges: 
            if privilege_ in removeFrom:
                removeFrom.remove(privilege_)
    
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
        
        persistedAce = PersistenceAce(self.principal.toPersistenceFormat())
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
        @raise PrincipalError: In case of an unsupported principal type.
        """
        
        principal = Principal.create(ace.principal)
        grantedPrivileges = list()
        for privilegeId in ace.grantedPrivileges:
            grantedPrivileges.append(getPrivilege(privilegeId))
        deniedPrivileges = list()
        for privilegeId in ace.deniedPrivileges:
            deniedPrivileges.append(getPrivilege(privilegeId))
        return AccessControlListEntry(principal, grantedPrivileges, deniedPrivileges)
