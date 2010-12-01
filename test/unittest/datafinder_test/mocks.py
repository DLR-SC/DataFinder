# pylint: disable=W0706
# $Filename$ 
# $Authors$
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#
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
This module implements general usable mock implementation for different aspects of 
the WebDAV library.
"""


__version__ = "$Revision-Id:$" 


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
