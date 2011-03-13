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


""" Tests the different property representations."""


import unittest

from datafinder.core.error import PropertyError
from datafinder.core.configuration.properties import constants
from datafinder.core.configuration.properties.property_definition import PropertyDefinition
from datafinder.core.configuration.properties import property_type


__version__ = "$Revision-Id:$" 


class PropertyTypeTestCase(unittest.TestCase):
    """ Some basic tests for properties. """
    
    def setUp(self):
        """ Initializes the property instance. """
    
        self._propertyDef = PropertyDefinition("name", constants.USER_PROPERTY_CATEGORY, property_type.StringType())
    
    def testSetNull(self):
        """ Tests the behavior when the the property must not be C{None}. """
        
        self.assertEqual(self._propertyDef.notNull, False)
        self._propertyDef.notNull = True
        
        try:
            self._propertyDef.validate(None)
            self.fail("Expected a PropertyTypeError indicating that value validation failed.")
        except PropertyError:
            self.assertEquals(self._propertyDef.notNull, True)
    
    def testValidate(self):
        """ Demonstrates the usage of validate method. """
        
        self._propertyDef.validate("value")
        self.assertRaises(PropertyError, self._propertyDef.validate, dict())
        self._propertyDef.validate(None)
        self._propertyDef.notNull = True
        self.assertRaises(PropertyError, self._propertyDef.validate, None)
            
    def testTypeAttribute(self):
        """ Demonstrates the usage of the type attribute. """
        
        self.assertEquals(self._propertyDef.type, property_type.StringType.name)
        try:
            self._propertyDef.type = ""
            self.fail("Expected an AttributeError")
        except AttributeError:
            self.assertEquals(self._propertyDef.type, property_type.StringType.name)
            
    def testRestrictions(self):
        """ Demonstrates the restriction attribute. """

        expectedRestrictions = dict()
        for key, value in expectedRestrictions.iteritems():
            self.assertTrue(key in self._propertyDef.restrictions)
            self.assertEquals(value, self._propertyDef.restrictions[key])

        anotherPropDef = PropertyDefinition("identifier", "category", property_type.StringType(10, 100))
        expectedRestrictions[constants.MINIMUM_LENGTH] = 10
        expectedRestrictions[constants.MAXIMUM_LENGTH] = 100
        for key, value in expectedRestrictions.iteritems():
            self.assertTrue(key in anotherPropDef.restrictions)
            self.assertEquals(value, anotherPropDef.restrictions[key])
        
    def testComparison(self):
        """ Demonstrates equality and inequality of property definitions. """
        
        self.assertEquals(self._propertyDef, self._propertyDef)
        
        other = PropertyDefinition("identifier", constants.USER_PROPERTY_CATEGORY, property_type.NumberType())
        self.assertNotEquals(self._propertyDef, other)
        
        other = PropertyDefinition("name", constants.USER_PROPERTY_CATEGORY, property_type.NumberType())
        self.assertEquals(self._propertyDef, other)

        other.namespace = "anothernamespace"
        self.assertNotEquals(self._propertyDef, other)
