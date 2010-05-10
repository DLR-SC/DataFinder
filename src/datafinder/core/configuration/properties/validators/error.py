#
# Created: 01.09.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: error.py 3722 2009-01-27 10:13:22Z lege_ma $ 
# 
# Copyright (C) 2003-2008 DLR/SISTEC, Germany
# 
# All rights reserved
# 
# http://www.dlr.de/datafinder/
#


""" 
Implements specific error class for this package.
"""


__version__ = "$LastChangedRevision: 3722 $"


class ValidationError(Exception):
    """ Class representing a validation error. """
    
    def __init__(self, errorMessage):
        """ 
        Constructor.
        
        @param errorMessage: The message describing the validation error.
        @type errorMessage: C{unicode}
        """
        
        Exception.__init__(self)
        self.errorMessage = errorMessage
