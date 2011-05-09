# pylint: disable=W0212
# W0212: For test reasons it is fine to access protected members.
#
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
Provides tests for the different property types.
"""


import datetime
import decimal
import unittest

from datafinder.core.configuration.properties import domain
from datafinder.core.configuration.properties import property_type, constants
from datafinder.core.error import ConfigurationError


__version__ = "$Revision-Id:$" 


class BasePropertyTestCase(unittest.TestCase):

    def setUp(self):
        """ Creates the test fixture. """
        
        self._propertyType = property_type.BasePropertyType(False)
        
    def testDefaultBehavior(self):
        """ Tests default data and method implementation. """
        
        self.assertFalse(self._propertyType.notNull)
        self.assertTrue(len(self._propertyType.restrictions) == 0)
        self.assertEquals(self._propertyType.fromPersistenceFormat("aValue"), "aValue")
        self.assertEquals(self._propertyType.toPersistenceFormat("aValue"), "aValue")
        
    def testValidate(self):
        """ Tests success and error cases. """
        
        self._propertyType.validate("")
        
        self._propertyType.notNull = True
        self.assertRaises(ValueError, self._propertyType.validate, None)


class StringPropertyTestCase(unittest.TestCase):

    def setUp(self):
        """ Creates the test fixture. """
        
        self._propertyType = property_type.StringType()
      
    def testDefaultBehavior(self):
        """ Tests default data settings. """
      
        self.assertEquals(len(self._propertyType.restrictions), 5)


class BooleanPropertyTestCase(unittest.TestCase):

    def setUp(self):
        """ Creates the test fixture. """
        
        self._propertyType = property_type.BooleanType()
    
    def testDefaultBehavior(self):
        """ Tests default data settings. """
      
        self.assertEquals(len(self._propertyType.restrictions), 0)


class NumberPropertyTestCase(unittest.TestCase):

    def setUp(self):
        """ Creates the test fixture. """
        
        self._propertyType = property_type.NumberType()
    
    def testDefaultBehavior(self):
        """ Tests default data settings. """
      
        self.assertEquals(len(self._propertyType.restrictions), 6)


class DatetimePropertyTestCase(unittest.TestCase):

    def setUp(self):
        """ Creates the test fixture. """
        
        self._propertyType = property_type.DatetimeType()
    
    def testDefaultBehavior(self):
        """ Tests default data settings. """
      
        self.assertEquals(len(self._propertyType.restrictions), 4)


class ListPropertyTestCase(unittest.TestCase):

    def setUp(self):
        """ Creates the test fixture. """
        
        allowedTypes = [property_type.StringType()]
        self._propertyType = property_type.ListType(allowedTypes)
        self.assertEquals(len(self._propertyType.restrictions), 3)
        self.assertEquals(len(self._propertyType.restrictions[constants.ALLOWED_SUB_TYPES]), 1)
        self.assertEquals(self._propertyType.restrictions["subTypes"], 
                          [subType.name for subType in allowedTypes])
        
        self._propertyType = property_type.ListType()
        self.assertEquals(len(self._propertyType.restrictions), 3)
        self.assertEquals(len(self._propertyType.restrictions[constants.ALLOWED_SUB_TYPES]), 5)

    def testFromPersistenceFormat(self):
        self._propertyType.fromPersistenceFormat(["", True])
        self.assertRaises(ValueError, self._propertyType.fromPersistenceFormat, [list()])

    def testToPersistenceFormat(self):
        self._propertyType.toPersistenceFormat(["", True])
        self.assertRaises(ValueError, self._propertyType.toPersistenceFormat, [dict()])


class _City(domain.DomainObject):    
    name = domain.DomainProperty(property_type.StringType(5), "", "City Name", "Name of the city.")
    zip = domain.DomainProperty(property_type.StringType(), "", "ZIP", "The postal code of the city.")
    
    def __init__(self, name="", zip_=""):
        domain.DomainObject.__init__(self)
        self.name = name
        self.zip = zip_

class _Test(domain.DomainObject):
    a = domain.DomainProperty(property_type.DomainObjectType(_City), _City("mmmmmm"))
    b = domain.DomainProperty(property_type.DomainObjectType(_City), _City("mmmmmm"))
    c = domain.DomainProperty(property_type.DomainObjectType(_City), _City("mmmmmm"))


class AnyPropertyTestCase(unittest.TestCase):

    def setUp(self):
        """ Creates the test fixture. """
        
        self._propType = property_type.AnyType()
        self.assertEquals(len(self._propType.restrictions), 1) # Allowed types
        self._successValues = [
            False, "hhh", u"hhh", 324234, 32.4234, decimal.Decimal(32),
            datetime.datetime(2008, 9, 9), [1, u"344", True]]

        allowedTypes = [property_type.DatetimeType()]
        propType = property_type.AnyType(allowedTypes)
        self.assertEquals(propType.restrictions, 
                          {"subTypes": [subType.name for subType in allowedTypes]})
    
    def testValidate(self):
        """ Tests default data settings. """
        
        # Success cases
        for value in self._successValues:
            self._propType.validate(value)
        self._propType.validate(property_type.UnknownDomainObject(dict()))
        self._propType.validate(["string", property_type.UnknownDomainObject(dict())])

        # As default no list of lists are supported
        self.assertRaises(
            ValueError, self._propType.validate, ["string", ["string", "string", False]])

    def testToPersistenceFormat(self):
        # Success cases
        for value in self._successValues:
            self.assertEquals(self._propType.toPersistenceFormat(value), value)
        
        # Unspecific domain properties are valid but cannot be stored
        self.assertRaises(
            ValueError, self._propType.toPersistenceFormat, _City("New York"))
        self.assertRaises(
            ValueError, self._propType.toPersistenceFormat, ["string", _City("New York")])
        # As default no list of lists are supported
        self.assertRaises(
            ValueError, self._propType.toPersistenceFormat, ["string", ["string", "string", False]])

    def testFromPersistenceFormat(self):
        # Success cases
        for value in self._successValues:
            self.assertEquals(self._propType.fromPersistenceFormat(value), value)
        test = {"a": {"name": "New York", "zip": "45667"},
                "b": {"name": "New England", "zip": "45667"},
                "c": {"name": "New Jersy", "zip": "45667"}}
        value = self._propType.fromPersistenceFormat(test)
        self.assertTrue(isinstance(value, property_type.UnknownDomainObject))
        self.assertEquals(repr(value), "representation: '%s'" % str(test))

        # As default no list of lists are supported
        self.assertRaises(
            ValueError, self._propType.fromPersistenceFormat, ["string", ["string", "string", False]])


class DomainObjectPropertyTestCase(unittest.TestCase):

    def setUp(self):
        self._propertyType = property_type.DomainObjectType(_City)
        self._unknownDomainObj = property_type.DomainObjectType()
        
    def testInit(self):
        """ Tests the initialization via class object and full dotted class name. """

        # Initialization via class object      
        cls = _City
        name = "datafinder_test.core.configuration.properties.property_type_test._City"
        propertyType = property_type.DomainObjectType(_City)
        self.assertEquals(propertyType.name, name)
        self.assertEquals(propertyType._cls, cls)
        
        # Initialization via full dotted class name      
        propertyType = property_type.DomainObjectType(name)
        self.assertEquals(propertyType.name, name)
        self.assertEquals(propertyType._cls, cls)
        
        # Initialization with full dotted name returns a class object
        # with another name.
        property_type.__import__ = lambda _, __, ___, ____: self.__module__
        property_type.getattr = lambda _, __: self.__class__
        self.assertEquals(property_type.DomainObjectType(name)._cls, 
                          property_type.UnknownDomainObject)
        property_type.__import__ = __import__
        property_type.getattr = getattr
        
        # Unknown domain objects      
        self.assertEquals(property_type.DomainObjectType("")._cls, 
                          property_type.UnknownDomainObject)
        self.assertEquals(property_type.DomainObjectType()._cls, 
                          property_type.UnknownDomainObject)
        
        
    def testValidate(self):
        city = _City("New York")
        self._propertyType.validate(city) # success
        # Unknown domain objects are valid 
        self._unknownDomainObj.validate(property_type.UnknownDomainObject(dict())) 
        
        self.assertRaises(ValueError, self._propertyType.validate, True) # Wrong value
        self.assertRaises(ValueError, self._unknownDomainObj.validate, _City()) # Wrong domain object
        self.assertRaises(ValueError, self._propertyType.validate, _City()) # City not valid
        # Non-domain object
        propType = property_type.DomainObjectType(list)
        self.assertRaises(ValueError, propType.validate, list())

    def testToPersistenceFormat(self):
        # Success
        expectedResult = {"name": "", "zip": ""}
        self.assertEquals(self._propertyType.toPersistenceFormat(_City()), expectedResult)
        # Unknown domain objects should not be stored
        self.assertRaises(ValueError, self._unknownDomainObj.toPersistenceFormat, 
                          property_type.UnknownDomainObject(dict()))
        # Value does not fit
        self.assertRaises(ValueError, self._propertyType.toPersistenceFormat, 
                          property_type.UnknownDomainObject(dict()))
        # Non-domain object
        propType = property_type.DomainObjectType(list)
        self.assertRaises(ValueError, propType.toPersistenceFormat, list())
        # None stays None
        self.assertEquals(self._propertyType.toPersistenceFormat(None), None)
    
    def testFromPersistenceFormat(self):
        persistedValue = {"name": "New York", "zip": "45667"}
        expectedResult = _City(persistedValue["name"], persistedValue["zip"])
        self.assertEquals(self._propertyType.fromPersistenceFormat(persistedValue), 
                          expectedResult)
        self.assertEquals(self._unknownDomainObj.fromPersistenceFormat(persistedValue), 
                          property_type.UnknownDomainObject(persistedValue))
        
        # Dictionary and domain object do not match
        self.assertRaises(ValueError, self._propertyType.fromPersistenceFormat, dict())
    
        # Invalid persisted objects
        self.assertRaises(ValueError, self._propertyType.fromPersistenceFormat, list())
        self.assertRaises(ValueError, self._propertyType.fromPersistenceFormat, "list()")
    
        # None stays None
        self.assertEquals(self._propertyType.fromPersistenceFormat(None), None)
        
        # Domain object with non-empty constructor
        class TheCity(_City):
            def __init__(self, name):
                _City.__init__(self, name, "zip")
        propertyType = property_type.DomainObjectType(TheCity)
        self.assertRaises(ValueError, propertyType.fromPersistenceFormat, persistedValue)


class HelperFunctionTestCase(unittest.TestCase):
    """ Tests the different module helper functions. """
    
    def testCreatePropertyType(self):
        # Standard property type
        self.assertEquals(property_type.createPropertyType("String").name, "String")
        # Domain property
        name = "datafinder_test.core.configuration.properties.property_type_test._City"
        self.assertEquals(property_type.createPropertyType(name)._cls, _City)
        # Non-existing domain property
        self.assertEquals(property_type.createPropertyType("")._cls, 
                          property_type.UnknownDomainObject)
        # Invalid restrictions
        self.assertRaises(ConfigurationError, property_type.createPropertyType, "String", {"a": 1})
        
    def testDeterminePropertyTypeConstant(self):
        self.assertEquals(property_type.determinePropertyTypeConstant(""), "String")
        name = "datafinder_test.core.configuration.properties.property_type_test._City"
        self.assertEquals(property_type.determinePropertyTypeConstant(_City()), name)
