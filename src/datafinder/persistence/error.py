#
# Created: 27.01.2009 mohr_se <steven.mohr@dlr.de>
# Changed: $Id: error.py 3882 2009-03-26 09:07:24Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Persistence errors
"""


__version__ = "$LastChangedRevision: 3882 $"


class PersistenceError(Exception):
    """
    Error class for the persistence level.
    Other error classes on the persistence level
    should be subclassed from this one.
    """

    pass
