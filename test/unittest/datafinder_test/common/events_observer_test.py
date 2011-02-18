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
tests the observer implementation of the datafinder
"""


__version__ = "$Revision-Id:$" 

import unittest

from datafinder.common.event_observer import Observable

#Test Modules     
class MyClass(object):
    """ Simple test class which gets observed. """
    
    def __init__(self):
        self._para = 2
    
    @Observable # Indicates an observable method
    @classmethod
    def do_it(cls, test, test2):
        return test * test2 * 2
    
class MyClassEvent(object):
    "TestEvent"  
    def __init__(self):
        pass    
    
    def register(self,observer, instance = False):
        """
        Register an Observer to this event. 
        To get an instance of the object: instance = True
        """
        if instance:
            setInstance = MyClass()
            setInstance.do_it += observer
            return setInstance
        else:
            MyClass.do_it += observer
    
    def unregister(self, observer, instance = None):
        if instance: 
            instance.do_it -= observer
        else:
            MyClass.do_it -= observer  
    
    
def consumer(args, kwargs, retVal):
    """ Just prints the arguments and result on console. """
    
    print args, kwargs, retVal


if __name__ == "__main__":
    # Register two class-specific observers
    MyClassEvent().register(consumer)
    #MyClassEvent().register(consumer)
    #MyClass.do_it += consumer
    
    c = MyClass()
   
    # Register a instance-specific observer
    c2 = MyClassEvent().register(consumer, True)
    print c.do_it(2, 4) # Two observers are called
    
    MyClass.do_it(2,4)   
    #c2.do_it += consumer
    print c2.do_it(2, 4) # Three observers are called
    
    # Remove a class specific observer
    MyClassEvent().unregister(consumer)
    print c.do_it(2, 4) # Just one observer is called
    print c2.do_it(2, 4)
    MyClassEvent().unregister(consumer, c2)
    print c2.do_it(2, 4)

    

  