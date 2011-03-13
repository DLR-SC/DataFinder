# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
#
# All rights reserved.
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#
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
Defines interface and default implementation for privilege-/ACL-related actions.
"""


from datafinder.persistence.privileges.constants import ALL_PRIVILEGE


__version__ = "$Revision-Id:$" 


class NullPrivilegeStorer(object):
    """ 
    Null pattern / default implementation of the privilege-/ACL-related interface.
    
    @note: Real implementations of this interface are raising errors of
           type L{PersistenceError<datafinder.persistence.error.PersistenceError>}
           to indicate problems.
    """
    
    def __init__(self, identifier):
        """ 
        Constructor. 
        
        @param identifier: The logical identifier of the associated item. 
                           This is usually the path relative to a root.
        @type identifier: C{unicode}
        """
        
        self.identifier = identifier
    
    def updateAcl(self, acl):
        """
        Updates the associated Access Control List (ACL).
        
        @param acl: Describes the ACL of the item. Every entry describes 
                    a list of granted/denied privileges of specific principal.
                    For defined privileges see L{datafinder.persistence.constants}.
        @type acl: C{list} of L{AccessControlEntry<datafinder.persistence.privileges.ace.AccessControlListEntry>}
        """
        
        pass
    
    def retrievePrivileges(self):
        """
        Determines the privileges that the current user owns regarding the associated item. 
        
        @return: List of granted privileges.
                 For defined privileges see L{datafinder.persistence.constants}.
        @rtype: C{list} of C{unicode}
        """
        
        self = self # silent pylint
        return [ALL_PRIVILEGE]
    
    def retrieveAcl(self):
        """
        Retrieve the ACL of the associated item.
        
        @return ACL of the item. Every entry describes 
                a list of granted/denied privileges of specific principal.
                For defined privileges see L{datafinder.persistence.constants}.
        @rtype C{list} of L{AccessControlEntry<datafinder.persistence.privileges.ace.AccessControlListEntry>}
        """
        
        self = self # silent pylint
        return list()
