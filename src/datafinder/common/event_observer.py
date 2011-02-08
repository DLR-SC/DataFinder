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
This module implements the observer pattern for the DataFinder. 
Events can be told, and listeners can listen to these events.
"""
import logging

__version__ = "$Revision-Id:$" 
_log = logging.getLogger("script")
    
class Observable(object):
    
    def __init__(self, method):
        """ Takes a bound method and makes it observable by other object. """
      
        self.classObservable = None # Class-specific observable instance, None-> it is the class-spcific one
        self.observers = list() # List of observers
        self.instance = None # Instance the method is bound to
        self.method = method # Method that is observed
        self.__doc__ = self.method.__doc__ # Documentation
        self.cls = None
        try: 
            self.name = " " + method.__name__ # Name that is used to attach observers to the instances
        except AttributeError:
            self.name = None
  
            
    def __add__(self, observer):
        """
        Registering an Listener
        @param eventName: Name of the event the listener is registered for
        @param callback: Function that is supposed to be called on firing the event
        """
        if not observer in self.observers:
            self.observers.append(observer)
        return self
     
    def __sub__(self, observer):
        """
        Unregister an Listener
        @param eventName: Name of the event the listener is registered for
        @param callback: Function that is supposed to be called on firing the event
        """
        try:
            self.observers.remove(observer)
        except ValueError:
            pass
        return self    
            
    def __call__(self, *args, **kwargs):
        """ Calls the observable method and handles observer notification. 
        TODO: Think of exception handling and threading issues.
        """
        
        if not hasattr(self.method, "__call__"):
            methodToCall = self.method.__get__(self.instance, self.cls)
            returnValue = methodToCall(*args, **kwargs)
        else:
            returnValue = self.method(self.instance, *args, **kwargs)
        
        if not self.classObservable is None: # Call all class-specific observers
            for observer in self.classObservable.observers:
                observer(args, kwargs, returnValue)
        for observer in self.observers: # Call the instance-specific observers
            observer(args, kwargs, returnValue)
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
