# pylint: disable-msg=W0613, R0201
# W0613 is disabled because the arguments are not required for provision of
# a default implementation but are required for documentation.
# R0201 is disabled for similar reasons.
#
# Created: 17.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: principalsearcher.py 3803 2009-02-20 16:26:50Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Defines interface and default implementation for principal search actions.
"""


__version__ = "$LastChangedRevision: 3803 $"


class NullPrincipalSearcher(object):
    """ 
    Null pattern / default implementation of the principal-search-interface.
    
    @note: Real implementations of this interface are raising errors of
           type L{PersistenceError<datafinder.persistence.error.PersistenceError>}
           to indicate problems.
    """
    
    def searchPrincipal(self, pattern, searchMode):
        """ 
        Retrieves principals matching the given restrictions.
        
        @param pattern: Principal name pattern.
        @type pattern: C{unicode}
        @param searchMode: Distinguishes search for users / groups.
        @type searchMode: C{unicode} @see L{Constants<definition<datafinder.persistence.constants>} 
        
        @return: Matched principals.
        @rtype: C{list} of L{Principal<datafinder.interface.principal_search.principal.Principal>}
        """
        
        return list()
