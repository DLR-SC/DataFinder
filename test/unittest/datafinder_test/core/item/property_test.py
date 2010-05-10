#
# Created: 10.03.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: property_test.py 4117 2009-05-27 11:12:39Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Provides tests for the property representation.
"""


import unittest

from datafinder.core.error import PropertyError
from datafinder.core.item.property import Property
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4117 $"
    
    
class _PropertyDefinitionMock(object):
    """ Mocks property definition for the creation test case. """
    
    defaultValue = None
    mock = None
    
    def validate(self, value):
        """ Mocks the validate method. """
        
        if not value == self.defaultValue:
            self.mock.validate(value)
    

class PropertyTestCase(unittest.TestCase):
    """ Provides test cases for the Property representation. """
    
    def setUp(self):
        """ Creates object under test. """
        
        self._propertyDefMock = SimpleMock(identifier="id")
        self._property = Property(self._propertyDefMock, None)
        
    def testNotPersistedValue(self):
        """ Shows the behavior with a value which is not in persistence format. """
        
        self.assertEquals(self._property.value, None)
        self._property.value = "Test"
        self.assertEquals(self._property.value, "Test")
        self.assertTrue(len(self._property.additionalValueRepresentations) == 0)
        
        self._propertyDefMock.error = PropertyError("", "")
        try:
            self._property.value = 56
            self.fail("MetadataError was not raised.")
        except PropertyError:
            self.assertEquals(self._property.value, "Test")
        
    def testCreate(self):
        """ Shows creation of a property from persistence format. """
        
        self._property = Property.create(self._propertyDefMock, SimpleMock([None]))
        self.assertEquals(self._property.value, None)
        self.assertTrue(len(self._property.additionalValueRepresentations) == 0)

        self._property = Property.create(self._propertyDefMock, SimpleMock([True, 0, "0"]))
        self.assertEquals(self._property.value, True)
        self.assertEquals(self._property.additionalValueRepresentations, [0, "0"])

        self._propertyDefMock.error = PropertyError("", "")
        propertyDefMock = _PropertyDefinitionMock()
        propertyDefMock.mock = self._propertyDefMock
        propertyDefMock.defaultValue = "Test"
        self._property = Property.create(propertyDefMock, SimpleMock([True, 0, "0"]))
        self.assertEquals(self._property.value, "Test")
        self.assertEquals(self._property.additionalValueRepresentations, list())

    def testComparison(self):
        """ Tests the comparison of two instances. """
        
        self.assertEquals(self._property, self._property)
        self.assertEquals(self._property, Property(self._property.propertyDefinition, "value"))
        self.assertNotEquals(self._property, Property(SimpleMock(), "value"))
