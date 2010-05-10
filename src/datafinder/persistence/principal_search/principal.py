#
# Created: 20.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: principal.py 3858 2009-03-16 09:51:00Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Defines data associated with a principal, i.e. user / role.
"""


from datafinder.persistence.principal_search import constants


__version__ = "$LastChangedRevision: 3858 $"


class Principal(object):
    """ Represents a principal. """
    
    def __init__(self, identifier, **kwargs):
        """ Constructor. """
        
        self.identifier = identifier
        self.type = constants.USER_PRINCIPAL_TYPE
        self.displayName = identifier
        self.memberof = list()
        self.__dict__.update(kwargs)
        
    def __cmp__(self, principal):
        """ Compares of two instances. """
        
        if self.identifier == principal.identifier \
           and self.type == principal.type \
           and self.displayName == principal.displayName:
            identical = True
            for item in self.memberof:
                if not item in principal.roles:
                    identical = False
            if identical:
                return 0
        return 1
