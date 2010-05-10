#
# Created: 01.06.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: property_definition_test.py 4117 2009-05-27 11:12:39Z schlauch $ 
# 
# Copyright (C) 2003-2008 DLR/SISTEC, Germany
# 
# All rights reserved
# 
# http://www.dlr.de/datafinder/
#


""" Tests the different property representations."""


import unittest

from datafinder.core.error import PropertyError
from datafinder.core.configuration.properties import constants
from datafinder.core.configuration.properties.property_definition import PropertyDefinition
from datafinder.core.configuration.properties import property_type


__version__ = "$LastChangedRevision: 4117 $"


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
        
        self.assertEquals(self._propertyDef.type, property_type.StringType.NAME)
        try:
            self._propertyDef.type = ""
            self.fail("Expected an AttributeError")
        except AttributeError:
            self.assertEquals(self._propertyDef.type, property_type.StringType.NAME)
            
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
