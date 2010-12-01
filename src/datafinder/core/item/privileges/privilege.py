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


from datafinder.core.error import CoreError


__version__ = "$Revision-Id:$" 


class _Privilege(object):
    """
    This class defines available properties of a privilege.
    The class mainly exists for documentation reasons and is intended
    to be replaced by named tuples when switching to Python 3.
    """
    
    def __init__(self, identifier, displayName, description):
        """
        Constructor.
        
        @param identifier: Identifier of the privilege.
        @type identifier: C{unicode}
        @param displayName: Identifier of the privilege.
        @type displayName: C{unicode}
        @param descriptiondentifier: Identifier of the privilege.
        @type description: C{unicode}
        """
        
        self.identifier = identifier
        self.displayName = displayName
        self.description = description
    

ALL_PRIVILEGE = _Privilege("____all____", "All", "Aggregates all available privileges.")
READ_PRIVILEGE = _Privilege("____read____", "Read", "Determines read access to an item.")
WRITE_PRIVILEGE = _Privilege("____write____", "Write", "Determines write access to an item.")
READ_PRIVILEGES_PRIVILEGE = _Privilege("____readprivileges____", "Read Privileges", "Determines reading item privileges.")
WRITE_PRIVILEGES_PRIVILEGE = _Privilege("____writeprivileges____", "Write Privileges", "Determines writing item privileges.")

PRIVILEGES = [ALL_PRIVILEGE, READ_PRIVILEGE, WRITE_PRIVILEGE, READ_PRIVILEGES_PRIVILEGE, WRITE_PRIVILEGES_PRIVILEGE]


def getPrivilege(identifier):
    """ 
    Creates a privilege from the persistence format.
    
    @param identifier: Privilege identifier.
    @type identifier: C{unicode} 
    """
    
    for privilege in PRIVILEGES:
        if privilege.identifier == identifier:
            return privilege 
    raise CoreError("The privilege '%s' is not supported." % identifier)
