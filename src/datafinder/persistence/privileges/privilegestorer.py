# pylint: disable-msg=R0201
# R0201 is disabled to provide a correct interface definition and default implementation.
# Usage of the @staticmehtod decorator would be confusing.
#
# Created: 17.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: privilegestorer.py 4075 2009-05-19 14:39:16Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Defines interface and default implementation for privilege-/ACL-related actions.
"""


from datafinder.persistence.privileges.constants import ALL_PRIVILEGE


__version__ = "$LastChangedRevision: 4075 $"


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
        
        return [ALL_PRIVILEGE]
    
    def retrieveAcl(self):
        """
        Retrieve the ACL of the associated item.
        
        @return ACL of the item. Every entry describes 
                a list of granted/denied privileges of specific principal.
                For defined privileges see L{datafinder.persistence.constants}.
        @rtype C{list} of L{AccessControlEntry<datafinder.persistence.privileges.ace.AccessControlListEntry>}
        """
        
        return list()
