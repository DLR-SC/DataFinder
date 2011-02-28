# $Filename$$
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
This module provides an annotation to make methods observable.. 
"""


import logging


__version__ = "$Revision-Id:$" 


_log = logging.getLogger("script")

    
class Observable(object):
    """ Implements the observable annotation for bound
    methods, static methods and class methods. """
        
    def __init__(self, method):
        """ Takes a method and makes it 
        observable by another object. """
      
        self.classObservable = None # Class-specific observable instance, None-> it is the class-spcific one
        self.callbacks = list() # List of observer functions / methods
        self.instance = None # Instance the method is bound to
        self.method = method # Method that is observed
        self.__doc__ = self.method.__doc__ # Documentation
        self.cls = None
        try: 
            self.name = " " + method.__name__ # Name that is used to attach callbacks to the instances
        except AttributeError:
            self.name = None
  
    def __add__(self, callback):
        """
        Registering a callback function which is called after method invocation.

        @param callback: Function that is supposed to be called on firing the event.
        @type callback: Function object which receives the following arguments:
                        args: Arguments the observed method received.
                        kwargs: Keyword arguments the observed method received.
                        returnValue: The returned value of the observed method.
                        error: Error which may be raised by the observed method.
        """

        if not callback in self.callbacks:
            self.callbacks.append(callback)
        return self
     
    def __sub__(self, callback):
        """
        Removes the callback function from the observed method.
        
        @param callback: Function that has been formerly registered.
        
        @raise ValueError: If the callback function has not been registered before.
        """

        self.callbacks.remove(callback)
        return self    
            
    def __call__(self, *args, **kwargs):
        """ Calls the observed method and handles callback notification. """
        
        error = None
        returnValue = None
        
        # call the method and handle error
        try:
            if not hasattr(self.method, "__call__"):
                methodToCall = self.method.__get__(self.instance, self.cls)
                returnValue = methodToCall(*args, **kwargs)
            else:
                if self.instance is None: # Simulate standard error if the instance is None
                    returnValue = self.method(*args, **kwargs)
                returnValue = self.method(self.instance, *args, **kwargs)
        except Exception, error_:
            error = error_

        # call back
        if not self.classObservable is None: # Call all class-specific callbacks
            for callback in self.classObservable.callbacks:
                callback(args, kwargs, returnValue, error)
        for callback in self.callbacks: # Call the instance-specific callbacks
            callback(args, kwargs, returnValue, error)
        
        # Raise error if exists
        if not error is None:
            raise error
        return returnValue
        
    def __get__(self, instance, cls):
        """ Returns the wrapped observed method. """
        
        observable = self #if instance is None the method is called from the class object
        self.instance = instance
        self.cls = cls    
        if not instance is None and not self.name is None: 
            try:
                observable = self.instance.__dict__[self.name] # Retrieve the cached observable from the instance properties
            except KeyError: # Create a new observable if it not exists
                observable = Observable(self.method)
                observable.classObservable = self
                observable.cls = cls
                observable.instance = instance
                self.instance.__dict__[self.name] = observable
        return observable
