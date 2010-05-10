# pylint: disable-msg=W0706
# W0706: It is ensured that self.error is not raised when it is None
#
# Created: 21.02.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: mocks.py 3932 2009-04-14 07:37:48Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
This module implements general usable mock implementation for different aspects of 
the WebDAV library.
"""


__version__ = "$LastChangedRevision: 3932 $"


class SimpleMock(object):
    """ Simple mock implementation. """
    
    def __init__(self, returnValue=None, error=None, methodNameResultMap=None, **kwargs):
        """ 
        Constructor. 
        
        @param returnValue: The value that is returned when any method is called.
        @type returnValue: C{object}
        @param error: Error that is raised when any method is called.
        @type error: C{Exception}
        @param methodNameResultMap: Maps a method name to the corresponding result (value or error).
        @type methodNameResultMap: C{dict} keys: C{unicode}, values: C{tuple} of {object}, C{Excpetion}
        """
        
        self.error = error
        self.value = returnValue
        self.methodNameResultMap = methodNameResultMap
        self.__dict__.update(kwargs)
         
    def __getattr__(self, name):
        """ Automatic delegation. """
        
        value = self.value
        error = self.error
        if not self.methodNameResultMap is None:
            if name in self.methodNameResultMap:
                value, error = self.methodNameResultMap[name]
        if not error is None:
            return self._raiseError(error)
        else:
            return self._returnValue(value)

    def __call__(self, *_, **__):
        """ Allows mocking of functions. """
        
        return self.__getattr__("")()

    @staticmethod
    def _returnValue(value):
        """ Returns function that returns the given value. """
        def __returnValue(*_, **__):
            """ Returns the value. """
            
            return value
        return __returnValue
    
    @staticmethod
    def _raiseError(error):
        """ Returns function that raises the given error. """
        def __raiseError(*_, **__):
            """ Raises an error. """
            
            raise error 
        return __raiseError

    def __copy__(self):
        """ Implements copying. """
        
        return self
    
    def __deepcopy__(self, _):
        """ Implements deep copying. """
        
        return self
