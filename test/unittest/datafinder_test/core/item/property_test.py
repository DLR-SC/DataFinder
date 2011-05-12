# $Filename$ 
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
Provides tests for the property representation.
"""


import unittest

from datafinder.core.error import PropertyError
from datafinder.core.item.property import Property
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 
    
    
class _PropertyDefinitionMock(object):
    """ Mocks property definition for the creation test case. """
    
    defaultValue = None
    mock = None
    
    def validate(self, value):
        if not value == self.defaultValue:
            self.mock.validate(value)
    
    def fromPersistenceFormat(self, _):
        self = self # silent pylint
        return True


class PropertyTestCase(unittest.TestCase):
    """ Provides test cases for the Property representation. """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._propertyDefMock = SimpleMock(identifier="id")
        self._property = Property(self._propertyDefMock, None)
        
    def testNotPersistedValue(self):
        """ Shows the behavior with a value which is not in persistence format. """
        
        # Setting a valid value
        self._propertyDefMock.value = "Test"
        self._property.value = "Test"
        self.assertEquals(self._property.toPersistenceFormat(), 
                          {self._property.identifier: self._property.value})
        
        # Setting an invalid value
        self._propertyDefMock.error = PropertyError("", "")
        self._property.value = 56
        self.assertRaises(PropertyError, self._property.toPersistenceFormat)
        
    def testCreate(self):
        """ Shows creation of a property from persistence format. """
        
        self._property = Property.create(self._propertyDefMock, SimpleMock([None]))
        self.assertEquals(self._property.value, None)

        self._propertyDefMock.value = True
        self._property = Property.create(self._propertyDefMock, SimpleMock([True, 0, "0"]))
        self.assertEquals(self._property.value, True)

        self._propertyDefMock.methodNameResultMap = \
            {"fromPersistenceFormat": (None, PropertyError("", ""))}
        self._propertyDefMock.defaultValue = "Test"
        self._property = Property.create(self._propertyDefMock, SimpleMock([True, 0, "0"]))
        self.assertEquals(self._property.value, "Test")
        
    def testComparison(self):
        """ Tests the comparison of two instances. """
        
        self.assertEquals(self._property, self._property)
        self.assertEquals(self._property, Property(self._property.propertyDefinition, "value"))
        self.assertNotEquals(self._property, Property(SimpleMock(), "value"))
        self.assertNotEquals(self._property, None)
        
    def testToPersistenceFormat(self):
        self.assertEquals(self._property.toPersistenceFormat(), 
                          {self._property.identifier: None})
        
        self._propertyDefMock.error = PropertyError("", "")
        self.assertRaises(PropertyError, self._property.toPersistenceFormat)

    def testRepresentation(self):
        self.assertEquals(repr(self._property), 
                          "%s: %s" % (repr(self._propertyDefMock), repr(None)))
