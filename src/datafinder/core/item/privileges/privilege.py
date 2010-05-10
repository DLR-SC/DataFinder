#
# Created: 12.03.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: privilege.py 3858 2009-03-16 09:51:00Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
The module defines available privileges.
"""


from datafinder.core.error import CoreError


__version__ = "$LastChangedRevision: 3858 $"


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
