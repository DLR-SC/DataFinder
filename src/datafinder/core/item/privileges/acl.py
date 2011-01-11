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
Represents an access control list (ACL) of an item.
"""


from datafinder.core.item.privileges.ace import AccessControlListEntry
from datafinder.core.item.privileges import privilege


__version__ = "$Revision-Id:$" 


class AccessControlList(object):
    """
    Represents an access control list (ACL) of an item.
    """
    
    # [0]->Required read privileges [1]->Required write privileges
    _CONTENT_PRIVS = ([privilege.READ_PRIVILEGE], [privilege.WRITE_CONTENT, 
                       privilege.ADD_ITEM, privilege.REMOVE_ITEM])
    _PROPERTIES_PRIVS = ([privilege.READ_PRIVILEGE], [privilege.WRITE_PROPERTIES]) 
    _ADMIN_PRIVS = ([privilege.READ_PRIVILEGES_PRIVILEGE], [privilege.WRITE_PRIVILEGES_PRIVILEGE])
    
    
    def __init__(self, aces=None):
        """
        Constructor.
        
        @param aces: Optional list of access control list entries.
        @type aces: C{list} of L{AccesControlListEntry<datafinder.core.item.privileges.ace.AccesControlListEntry>}
        """
        
        self._aces = dict()
        
        self._principalOrder = list()
        if not aces is None:
            for ace in aces:
                self._aces[ace.principal] = ace
                self._principalOrder.append(ace.principal)
        
    def __getPrincipals(self):
        """ Getter for the principals. """
        
        return self._principalOrder[:]
    
    principals = property(__getPrincipals)
        
    def grantPrivilege(self, principal, priv):
        """ 
        Grants a privilege to a user / role.
        
        @param principal: User / role the privilege is granted.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        @param priv: Granted privilege.
        @type priv: L{privilege constants<datafinder.core.item.privileges.privilege>.
        """
    
        self._addAce(principal)    
        self._aces[principal.identifier].grantPrivilege(priv)

    def addDefaultPrincipal(self, principal):
        """ Adds the principal with default access levels 
        Content: Read-only, Properties: Read-Only, Administration: None
        If the principal has been already added nothing is changed.
        
        @param principal: User / role.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        """
    
        self._addAce(principal, True)
        
    def _addAce(self, principal, setDefaultAccessLevels=False):
        """ Adds an ACE for the given principal. """
        
        if not principal.identifier in self._aces:
            self._aces[principal.identifier] = AccessControlListEntry(principal)
            self._principalOrder.append(principal)
            if setDefaultAccessLevels:
                self.setContentAccessLevel(principal, privilege.READ_ONLY_ACCESS_LEVEL)
                self.setPropertiesAccessLevel(principal, privilege.READ_ONLY_ACCESS_LEVEL)
                self.setAministrationAccessLevel(principal, privilege.NONE_ACCESS_LEVEL)
            
    def denyPrivilege(self, principal, priv):
        """ 
        Denies a privilege for a user / role.
        
        @param principal: User / role the privilege is granted.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        @param priv: Denied privilege.
        @type priv: L{privilege constants<datafinder.core.item.privileges.privilege>.
        """
        
        self._addAce(principal)
        self._aces[principal.identifier].denyPrivilege(priv)

    def getGrantedPrivileges(self, principal):
        """ 
        Returns the privileges granted to a user / role.
        
        @param principal: User / role.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        
        @return: Set of granted privileges.
        @rtype: C{set} of L{privilege constants<datafinder.core.item.privileges.privilege>.  
        
        @raise ValueError: If the principal does not exist.
        """
        
        privileges = set()
        if principal.identifier in self._aces:
            privileges = self._aces[principal.identifier].grantedPrivileges
        else:
            raise ValueError("The principal '%s' is not defined." % principal.displayName)
        return privileges
    
    def getDeniedPrivileges(self, principal):
        """ 
        Returns the privileges denied for a user / role.
        
        @param principal: User / role.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        
        @return: Set of denied privileges.
        @rtype: C{set} of L{privilege constants<datafinder.core.item.privileges.privilege>.  
        
        @raise ValueError: If the principal does not exist.
        """

        privileges = set()
        if principal.identifier in self._aces:
            privileges = self._aces[principal.identifier].deniedPrivileges
        else:
            raise ValueError("The principal '%s' is not defined." % principal.displayName)
        return privileges

    def setContentAccessLevel(self, principal, level):
        """ Sets the access level of the principal
        concerning the item content.
        
        @param principal: User / role.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        @param level: Access level constant.
        @type level: L{_AccessLevel<datafinder.core.item.privileges.privilege._AccessLevel>}
        """
        
        self._setAccessLevel(principal, level, self._CONTENT_PRIVS)

    def contentAccessLevel(self, principal):
        """ Returns the access level of the principal
        concerning the item content.
        
        @param principal: User / role.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        
        @return: Access level constant.
        @rtype: L{_AccessLevel<datafinder.core.item.privileges.privilege._AccessLevel>}
        
        @raise ValueError: If the principal does not exist.
        """
        
        return self._getAccessLevel(principal, self._CONTENT_PRIVS)

    def _setAccessLevel(self, principal, level, requiredPrivs):
        """ Sets the access level. """
        
        self._addAce(principal)
        if level == privilege.NONE_ACCESS_LEVEL:
            for priv in requiredPrivs[0] + requiredPrivs[1]:
                self._aces[principal.identifier].denyPrivilege(priv)
        elif level == privilege.READ_ONLY_ACCESS_LEVEL:
            for priv in requiredPrivs[0]:
                self._aces[principal.identifier].grantPrivilege(priv)
            for priv in requiredPrivs[1]:
                self._aces[principal.identifier].denyPrivilege(priv)
        else: # Full access
            for priv in requiredPrivs[0] + requiredPrivs[1]:
                self._aces[principal.identifier].grantPrivilege(priv)

    def _getAccessLevel(self, principal, requiredPrivs):
        """ Determines the access level. """
        
        if not principal.identifier in self._aces:
            raise ValueError("The principal '%s' is not defined." % principal.displayName)
        grantedPrivileges = list()
        for priv in self._aces[principal.identifier].grantedPrivileges:
            grantedPrivileges += [priv] + priv.aggregatedPrivileges 

        hasReadingAccess = True
        for priv in requiredPrivs[0]:
            if not priv in grantedPrivileges:
                hasReadingAccess = False
        hasWritingAccess = True
        for priv in requiredPrivs[1]:
            if not priv in grantedPrivileges:
                hasWritingAccess = False
        
        if hasReadingAccess and hasWritingAccess:
            contentAccessLevel = privilege.FULL_ACCESS_LEVEL
        elif hasReadingAccess:
            contentAccessLevel = privilege.READ_ONLY_ACCESS_LEVEL
        else:
            contentAccessLevel = privilege.NONE_ACCESS_LEVEL
        return contentAccessLevel

    def setPropertiesAccessLevel(self, principal, level):
        """ Sets the access level of the principal
        concerning the item properties.
        
        @param principal: User / role.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        @param level: Access level constant.
        @type level: L{_AccessLevel<datafinder.core.item.privileges.privilege._AccessLevel>}
        """
        
        self._setAccessLevel(principal, level, self._PROPERTIES_PRIVS)

    def propertiestAccessLevel(self, principal):
        """ Returns the access level of the principal
        concerning the item properties.
        
        @param principal: User / role.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        
        @return: Access level constant.
        @rtype: L{_AccessLevel<datafinder.core.item.privileges.privilege._AccessLevel>}
        
        @raise ValueError: If the principal does not exist.
        """
        
        return self._getAccessLevel(principal, self._PROPERTIES_PRIVS)
    
    def setAministrationAccessLevel(self, principal, level):
        """ Sets the access level of the principal
        concerning the item administration.
        
        @param principal: User / role.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        @param level: Access level constant.
        @type level: L{_AccessLevel<datafinder.core.item.privileges.privilege._AccessLevel>}
        """
        
        self._setAccessLevel(principal, level, self._ADMIN_PRIVS)

    def aministrationAccessLevel(self, principal):
        """ Returns the access level of the principal
        concerning the item administration.
        
        @param principal: User / role.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        
        @return: Access level constant.
        @rtype: L{_AccessLevel<datafinder.core.item.privileges.privilege._AccessLevel>}
        
        @raise ValueError: If the principal does not exist.
        """
        
        return self._getAccessLevel(principal, self._ADMIN_PRIVS)
    
    def clearPrivileges(self, principal):
        """ Removes privilege definition of the given
        principal. If the principal does not exist no 
        error will be triggered.
        
        @param principal: The user/group which privileges shall be reset.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        """
        
        if principal.identifier in self._aces:
            del self._aces[principal.identifier]
            self._principalOrder.remove(principal)
            
    def setIndex(self, principal, position):
        """ Sets the index of the given principal.
        
        @param principal: The user/group whose position shall be set.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}
        @param position: The new positional index.
        @type position: C{int}
        
        @raise ValueError: If the principal does not exist.
        """
        
        self._principalOrder.remove(principal)
        self._principalOrder.insert(position, principal)
    
    def getIndex(self, principal):
        """ Returns the index of the given principal. 

        @param principal: The user/group whose position shall be determined.
        @type principal: L{Principal<datafinder.core.item.privileges.principal.Principal>}

        @return: The positional index.
        @rtype: C{int}
        
        @raise ValueError: If the principal does not exist.
        """
        
        if not principal in self._principalOrder:
            raise ValueError("The principal '%s' is not defined." % principal.displayName)
        else:
            return self._principalOrder.index(principal)

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
        @raise PrincipalError: In case of an unsupported principal type.
        """
        
        mappedAces = list()
        for ace in aces:
            mappedAces.append(AccessControlListEntry.create(ace))
        return AccessControlList(mappedAces)

    def __cmp__(self, other):
        """ Compares two ACLs. """
        # TODO: ensure that the order is correct
        result = 0
        if len(self.principals) != len(other.principals):
            result = 1
        else:
            for index, principal in enumerate(self.principals):
                if principal != other.principals[index]:
                    result = 1
                    break
                if self.getGrantedPrivileges(principal) != other.getGrantedPrivileges(principal) \
                   or self.getDeniedPrivileges(principal) != other.getDeniedPrivileges(principal):
                    result = 1
                    break
        return result
