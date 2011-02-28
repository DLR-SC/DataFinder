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
Tests the observer implementation.
"""


import unittest

from datafinder.common.event_observer import Observable


__version__ = "$Revision-Id:$" 


class _TestClass(object):
    """ Simple test class which gets observed. """
    
    _clsParameter = 2
    
    def __init__(self):
        self._parameter = 2
    
    @Observable
    def doItBound(self, test):
        return test * self._parameter

    @Observable
    @staticmethod
    def doItStatic(test):
        return test * 2
    
    @Observable
    @classmethod
    def doitClass(cls, test):
        return test * cls._clsParameter


class _Consumer(object):
    """ Simple test consumer for events. """
    
    def __init__(self):
        self.params = None
        
        
    def testConsumer(self, args, kwargs, returnValue, error):
        """ Just sets arguments. """
    
        self.params = args, kwargs, returnValue, error


class ObserverTestCase(unittest.TestCase):
    """
    Test cases of the observer mechanism.
    """

    def setUp(self):
        """ Creates the observed object. """
        
        self._consumer = _Consumer()
        self._observedInstance = _TestClass()
        
    def testCallableHandling(self):
        """ Tests adding and removing of callbacks. """
        
        # Standard mechanism
        _TestClass.doItBound += self._consumer.testConsumer
        _TestClass.doItStatic += self._consumer.testConsumer
        _TestClass.doitClass += self._consumer.testConsumer
        self._observedInstance.doItBound += self._consumer.testConsumer
        
        _TestClass.doItBound -= self._consumer.testConsumer
        _TestClass.doItStatic -= self._consumer.testConsumer
        _TestClass.doitClass -= self._consumer.testConsumer
        self._observedInstance.doItBound -= self._consumer.testConsumer
        
        # Removing not registered callback
        try:
            self._observedInstance.doItBound -= self._consumer.testConsumer
            self.fail("ValueError not raised")
        except ValueError:
            self.assertTrue(True)
        try:
            _TestClass.doItBound -= self._consumer.testConsumer
            self.fail("ValueError not raised")
        except ValueError:
            self.assertTrue(True)
        
        # Adding a callback to static method (same for class) of an instance
        self._observedInstance.doItStatic += self._consumer.testConsumer
        self._observedInstance.doItStatic -= self._consumer.testConsumer
        self._observedInstance.doItStatic += self._consumer.testConsumer
        _TestClass.doItStatic -= self._consumer.testConsumer
        
    def testCalling(self):
        """ Test the invocation of the observed methods. """
        
        # Adding callbacks and creating an additional consumer
        anotherConsumer = _Consumer()
        _TestClass.doItBound += self._consumer.testConsumer
        _TestClass.doItStatic += self._consumer.testConsumer
        
        # Success case
        self._observedInstance.doItBound += anotherConsumer.testConsumer
        self._observedInstance.doItBound(2)
        self.assertEquals(anotherConsumer.params, ((2,), {}, 4, None))
        self.assertEquals(self._consumer.params, ((2,), {}, 4, None))
        self._observedInstance.doItStatic(4)
        self.assertEquals(self._consumer.params, ((4,), {}, 8, None))
        _TestClass.doItStatic(2)
        self.assertEquals(self._consumer.params, ((2,), {}, 4, None))
        
        # Error case
        self.assertRaises(TypeError, _TestClass.doItBound, 2)
        self.assertEquals(self._consumer.params[3].__class__, TypeError)
