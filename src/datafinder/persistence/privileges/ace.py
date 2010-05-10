#
# Created: 20.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: ace.py 3824 2009-03-01 13:56:03Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Defines the access control list entry representation.
"""


__version__ = "$LastChangedRevision: 3824 $"


class AccessControlListEntry(object):
    """ Defines the access control list entry representation. """
    
    def __init__(self, principal, **kwargs):
        """ 
        Constructor. 
        
        @param principal: Principal the ACE definition is associated with.
        @type principal: L{Principal<datafinder.persistence.principal_search.principal.Principal>}
        """
        
        self.principal = principal
        self.grantedPrivileges = list()
        self.deniedPrivileges = list()
        self.__dict__.update(kwargs)
        
    def __cmp__(self, other):
        """ Compares two access control lists. """
        
        if self.principal == other.principal \
           and self.grantedPrivileges == other.grantedPrivileges \
           and self.deniedPrivileges == other.deniedPrivileges:
            return 1
        else:
            return 0
