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
The module defines available privileges.
"""


from datafinder.core.error import PrivilegeError
from datafinder.persistence.privileges import constants


__version__ = "$Revision-Id:$" 


class _Privilege(object):
    """
    This class defines available properties of a privilege.
    The class mainly exists for documentation reasons and is intended
    to be replaced by named tuples when switching to Python 3.
    """
    
    def __init__(self, identifier, displayName, description, aggregatedPrivileges=None):
        """
        Constructor.
        
        @param identifier: Identifier of the privilege.
        @type identifier: C{unicode}
        @param displayName: Display name of the privilege.
        @type displayName: C{unicode}
        @param description: Describes the purpose of the privilege. 
        @type description: C{unicode}
        @param aggregatedPrivileges: Directly aggregated privileges.
        @type aggregatedPrivileges: C{list} of L{_Privilege<datafinder.core.item.privileges.privilege._Privilege>}
        """
        
        self.identifier = identifier
        self.displayName = displayName
        self.description = description
        self.aggregatedPrivileges = aggregatedPrivileges
        
        if self.aggregatedPrivileges is None:
            self.aggregatedPrivileges = list()
        else:
            for privilege in aggregatedPrivileges:
                self.aggregatedPrivileges.extend(privilege.aggregatedPrivileges)

    def __repr__(self):
        """ Determines the string representation. """
        
        return self.displayName

    def __cmp__(self, other):
        """ Compares two instances. """
        
        return cmp(self.identifier, other.identifier)
    
    def __hash__(self):
        """ Calculates has value in accordance to comparison. """
        
        return id(self.identifier)


REMOVE_ITEM = _Privilege(constants.REMOVE_ITEM_PRIVILEGE, "Remove Item", "Determines removal of items.")
ADD_ITEM = _Privilege(constants.ADD_ITEM_PRIVILEGE, "Add Item", "Determines adding of items.")
WRITE_PROPERTIES = _Privilege(constants.WRITE_PROPERTIES_PRIVILEGE, "Write Properties", "Determines modification of properties.")
WRITE_CONTENT = _Privilege(constants.WRITE_CONTENT_PRIVILEGE, "Write Content", "Determines modification of the item content.")
WRITE_PRIVILEGE = _Privilege(constants.WRITE_PRIVILEGE, "Write", "Aggregates all modification privileges.",
                             [WRITE_CONTENT, WRITE_PROPERTIES, ADD_ITEM, REMOVE_ITEM])

READ_PRIVILEGES_PRIVILEGE = _Privilege(constants.READ_PRIVILEGES_PRIVILEGE, "Read Privileges", "Determines reading of item privileges.")
WRITE_PRIVILEGES_PRIVILEGE = _Privilege(constants.WRITE_PRIVILEGES_PRIVILEGE, "Write Privileges", "Determines writing of item privileges.")
READ_USER_PRIVILEGES_PRIVILEGE = _Privilege(constants.READ_USER_PRIVILEGES_PRIVILEGE, "Read User Privileges", 
                                            "Determines reading of the current user privileges.")

READ_PRIVILEGE = _Privilege(constants.READ_PRIVILEGE, "Read", "Determines reading of the item content and its properties.")

ALL_PRIVILEGE = _Privilege(constants.ALL_PRIVILEGE, "All", "Aggregates all available privileges.",
                           [READ_PRIVILEGE, READ_PRIVILEGES_PRIVILEGE, WRITE_PRIVILEGE, 
                            WRITE_PRIVILEGES_PRIVILEGE, READ_USER_PRIVILEGES_PRIVILEGE])


PRIVILEGES = [ALL_PRIVILEGE] + ALL_PRIVILEGE.aggregatedPrivileges


def getPrivilege(identifier):
    """ 
    Creates a privilege from the persistence format.
    
    @param identifier: Privilege identifier.
    @type identifier: C{unicode} 
    """
    
    for privilege in PRIVILEGES:
        if privilege.identifier == identifier:
            return privilege 
    raise PrivilegeError("The privilege '%s' is not supported." % identifier)


class _AccessLevel(object):
    """
    This class defines generally available access levels.
    Access level correspond to the item aspects content, properties, and administration.
    They are introduced to simplify the privilege handling in context of these item aspects
    """
    
    def __init__(self, identifier, displayName, description):
        """
        Constructor.
        
        @param identifier: Identifier of the access level.
        @type identifier: C{unicode}
        @param displayName: Display name of the access level.
        @type displayName: C{unicode}
        @param description: Describes the purpose of the access level. 
        @type description: C{unicode}
        """
        
        self.identifier = identifier
        self.displayName = displayName
        self.description = description
        
    def __str__(self):
        """ Determines the string representation. """
        
        return self.displayName

    __repr__ = __str__


NONE_ACCESS_LEVEL = _AccessLevel("____none____", "None", "Neither reading nor writing access.")
READ_ONLY_ACCESS_LEVEL = _AccessLevel("____read-only____", "Read-Only", "Only reading access.")
FULL_ACCESS_LEVEL = _AccessLevel("____full____", "Full", "Reading and writing access.")
ACCESS_LEVELS = [NONE_ACCESS_LEVEL, READ_ONLY_ACCESS_LEVEL, FULL_ACCESS_LEVEL]
