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
    
class EventParent:
    
    def __init__(self):
        self._observers = []
        
    def register(self, observer):
        """
        Registering an Listener
        @param eventName: Name of the event the listener is registered for
        @param callback: Function that is supposed to be called on firing the event
        """
        if not observer in self._observers:
            self._observers.append(observer)
    
    def unregister(self, observer):
        """
        Unregister an Listener
        @param eventName: Name of the event the listener is registered for
        @param callback: Function that is supposed to be called on firing the event
        """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
            
            
   
    def fireEvent(self, modifier= None):
        """
        Sending an information to all listeners registered for an event
        @param eventName: Name of the event the listener is registered for
        @param callback: Function that is supposed to be called on firing the event
        """
        for observer in self._observers:
            if modifier != observer:
                observer._callback(self)
 
 #
 #Things to be implemented into another class for the Observer Pattern
 #           
    
class Event(EventParent):
    '''
    Must be added to the item.factory or other factories, elements...  
    '''  
    def __init__(self, name, stuff=None):
        EventParent.__init__(self)
        self.name = name
        self.stuff = stuff

    def __str__(self):
        return '%s(%s)'% (self.name, self.stuff)
    


class Listener:
    """
    Module template for implementing a listener, that can listens on an event
    """
        
    def _callback(self, subject): 
        print "something called me"


def getEvent(): 
    return Event("TestEvent")

