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
Maps the interface-specific privilege definition to the WebDAV-specific one and vice versa.
"""


import os

from webdav.Constants import TAG_ALL, TAG_READ, TAG_WRITE, \
                             TAG_WRITE_CONTENT, TAG_WRITE_PROPERTIES, \
                             TAG_BIND, TAG_UNBIND, \
                             TAG_WRITE_ACL, TAG_READ_ACL, TAG_READ_CURRENT_USER_PRIVILEGE_SET, \
                             TAG_AUTHENTICATED, TAG_UNAUTHENTICATED, TAG_OWNER
from webdav.acp import ACL, ACE, Principal, GrantDeny, Privilege

from datafinder.persistence.error import PersistenceError
from datafinder.persistence.principal_search import constants as principal_constants
from datafinder.persistence.principal_search import principal
from datafinder.persistence.privileges import constants, ace


__version__ = "$Revision-Id:$" 


# maps WebDAV specific principals to defined principals
_webdavToGeneralPrincipalMap = {TAG_ALL: principal_constants.ALL_PRINCIPAL,
                                TAG_AUTHENTICATED: principal_constants.AUTHENTICATED_PRINCIPAL,
                                TAG_UNAUTHENTICATED: principal_constants.UNAUTHENTICATED_PRINCIPAL,
                                TAG_OWNER: principal_constants.OWNER_PRINCIPAL}
_generalToWebdavPrincipalMap = dict(zip(_webdavToGeneralPrincipalMap.values(), 
                                        _webdavToGeneralPrincipalMap.keys()))

# maps WebDAV specific privilege constants to defined privileges
_webdavToGeneralPrivilegeMap = {TAG_ALL: constants.ALL_PRIVILEGE,
                                TAG_WRITE: constants.WRITE_PRIVILEGE,
                                TAG_WRITE_CONTENT: constants.WRITE_CONTENT_PRIVILEGE,
                                TAG_WRITE_PROPERTIES: constants.WRITE_PROPERTIES_PRIVILEGE,
                                TAG_BIND: constants.ADD_ITEM_PRIVILEGE,
                                TAG_UNBIND: constants.REMOVE_ITEM_PRIVILEGE,
                                TAG_READ: constants.READ_PRIVILEGE,
                                TAG_WRITE_ACL: constants.WRITE_PRIVILEGES_PRIVILEGE,
                                TAG_READ_ACL: constants.READ_PRIVILEGES_PRIVILEGE,
                                TAG_READ_CURRENT_USER_PRIVILEGE_SET: constants.READ_USER_PRIVILEGES_PRIVILEGE}
_generalToWebdavPrivilegeMap = dict(zip(_webdavToGeneralPrivilegeMap.values(), 
                                        _webdavToGeneralPrivilegeMap.keys()))


class PrivilegeMapper(object):
    """ Implements mapping of privileges from the interface-specific to the WebDAV-specific format. """
    
    def __init__(self, userUrl, groupUrl):
        """ 
        Constructor. 
        
        @param userUrl: URL points to a collection containing the user principals.
        @type userUrl: C{unicode}
        @param userUrl: URL points to a collection containing the group principals.
        @type userUrl: C{unicode}
        """
        
        self._userUrl = userUrl
        self._groupUrl = groupUrl
        
    def mapAcl(self, acl):
        """ 
        Maps the given ACL in the interface format to the WebDAV-library-specific format. 
        
        @param acl: ACL in interface representation.
        @param acl: C{list} of L{AccessControlListEntry<datafinder.persistence.
        privileges.ace.AccessControlListEntry>}
        
        @return: ACL in WebDAV-specific format.
        @rtype: L{ACL<webdav.acp.Acl.ACL>}
        """
        
        persistenceAces = list()
        for ace_ in acl:
            persistenceAce = self._createAce(ace_.principal, ace_.grantedPrivileges, True)
            if not persistenceAce is None:
                persistenceAces.append(persistenceAce)
            persistenceAce = self._createAce(ace_.principal, ace_.deniedPrivileges, False)
            if not persistenceAce is None:
                persistenceAces.append(persistenceAce)
        return ACL(aces=persistenceAces)
            
    def _createAce(self, principal_, privileges, isGranted):
        """ Prepares a WebDAV-specific access control element. """
        
        ace_ = None
        if len(privileges) > 0:
            grantDeny = GrantDeny()
            if isGranted:
                grantDeny.setGrant()
            else:
                grantDeny.setDeny()
            grantDeny.addPrivileges(self._mapPrivileges(privileges))
            mappedPrincipal = self._mapPrincipal(principal_)
            ace_ = ACE(principal=mappedPrincipal, grantDenies=[grantDeny])
        return ace_    
    
    def _mapPrincipal(self, principal_):
        """ Maps the interface-specific principal representation to the WebDAV-specific. """
        
        if principal_.identifier in _generalToWebdavPrincipalMap.keys():
            mappedPrincipal = Principal()
            mappedPrincipal.property = _generalToWebdavPrincipalMap[principal_.identifier]
        else:
            if principal_.type == principal_constants.USER_PRINCIPAL_TYPE:
                principalUrl = self._userUrl + principal_.identifier
            else:
                principalUrl = self._groupUrl + principal_.identifier
            mappedPrincipal = Principal(principalURL=principalUrl)
        return mappedPrincipal
            
    @staticmethod
    def _mapPrivileges(privilegeConstants):
        """ Maps interface-specific privilege constants to WebDAV-library constants. """
        
        webdavPrivileges = list()
        for privilegeConstant in privilegeConstants:
            try:
                webdavPrivilegeConstant = _generalToWebdavPrivilegeMap[privilegeConstant]
            except KeyError:
                errorMessage = "Unsupported privilege '%s' was found!" % privilegeConstant
                raise PersistenceError(errorMessage)
            else:
                webdavPrivileges.append(Privilege(privilege=webdavPrivilegeConstant))
        return webdavPrivileges
    
    def mapPersistenceAcl(self, acl):
        """ 
        Maps an ACL in WebDAV-specific format to the interface-specific format.
        
        @param acl: ACL in WebDAV-specific format.
        @param acl: L{ACL<webdav.acp.Acl.ACL>}
        
        @return: ACL in interface representation.
        @rtype: C{list} of L{AccessControlListEntry<datafinder.persistence.
        privileges.ace.AccessControlListEntry>}
        """
        
        mappedAcl = list()
        joinedAcl = acl.joinGrantDeny() 
        for ace_ in joinedAcl.aces:
            if ace_.inherited is None:
                grantedPrivileges = list()
                deniedPrivileges = list()
                tmpList = None
                for grantDeny in ace_.grantDenies:
                    if grantDeny.isGrant():
                        tmpList = grantedPrivileges
                    else:
                        tmpList = deniedPrivileges
                    tmpList.extend(self.mapPersistencePrivileges(grantDeny.privileges))
                mappedPrincipal = self._mapPersistencePrincipal(ace_.principal)
                mappedAce = ace.AccessControlListEntry(mappedPrincipal, grantedPrivileges=grantedPrivileges, 
                                                       deniedPrivileges=deniedPrivileges)
                mappedAcl.append(mappedAce)
        return mappedAcl
    
    @staticmethod
    def mapPersistencePrivileges(privileges):
        """ 
        Maps privileges in the WebDAV-specific format to the interface representation.
        @note: Unsupported WebDAV privileges are irgnored.
        
        @param privileges: Privileges in WebDAV-specific format.
        @type privileges: C{list} of L{Privilege<webdav.acp.Privilege.Privilege>}
        
        @return: Privileges in interface format.
        @rtype: C{list} of C{unicode}
        @note: Privilege constants defined {here<datafinder.persistence.privileges.constants>}.
        """
        
        mappedPrivileges = list()
        for privilege in privileges:
            if _webdavToGeneralPrivilegeMap.has_key(privilege.name): # unsupported WebDAV privileges are ignored
                privilegeConstant = _webdavToGeneralPrivilegeMap[privilege.name]
                mappedPrivileges.append(privilegeConstant)
        return mappedPrivileges
    
    def _mapPersistencePrincipal(self, principal_):
        """ Maps the WebDAV representation of a principal to the interface-specific. """
        
        mappedPrincipal = principal.Principal(None)
        if not principal_.property is None and principal_.property in _webdavToGeneralPrincipalMap.keys():
            mappedPrincipal = principal.Principal(_webdavToGeneralPrincipalMap[principal_.property], 
                                                  type=principal_constants.GROUP_PRINCIPAL_TYPE)
        elif not principal_.principalURL is None:
            if self._userUrl in principal_.principalURL:
                principalType = principal_constants.USER_PRINCIPAL_TYPE
            else:
                principalType = principal_constants.GROUP_PRINCIPAL_TYPE
            mappedPrincipal = principal.Principal(os.path.basename(principal_.principalURL), type=principalType)
        return mappedPrincipal
