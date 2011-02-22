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

from datafinder.core.configuration.properties import property_type
from datafinder.core.configuration.properties.property_definition import PropertyDefinition
from datafinder.core.configuration.properties.validators.error import ValidationError
from datafinder.core.error import PropertyError
from datafinder.core.item.property import Property
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 
    
    
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
        
        propertyDef = PropertyDefinition("identifier", "category", property_type.ObjectType("datafinder_test.core.item.property_test.AuthorPropertyMock"))
        propertyDef.defaultValue = "Test"
        self._property = Property.create(propertyDef, SimpleMock([{"firstName": "Max", "lastName": "Muster", "email": "muster@gmail.com", \
                                                                   "address": {"street": "Teststreet", "city": "New York"}}]))
        self.assertEquals(self._property.value, {"firstName": "Max", "address": {"city": "New York", "street": "Teststreet"}, "lastName": "Muster", \
                                                 "email": "muster@gmail.com"})
        self.assertEquals(self._property.additionalValueRepresentations, list())
        
        self.assertRaises(PropertyError, Property.create, propertyDef, SimpleMock([{"lastName": "Muster", "email": "muster@gmail.com", \
                                                                                    "address": {"street": "Teststreet", "city": "New York"}}]))
        self.assertRaises(PropertyError, Property.create, propertyDef, SimpleMock([{"firstName": "Max", "lastName": "Muster", "email": "muster@gmail.com", \
                                                                                    "address": {"street": "Teststreet"}}]))
        self.assertRaises(PropertyError, Property.create, propertyDef, SimpleMock([{"name": "Max", "lastName": "Muster", "email": "muster@gmail.com", \
                                                                                    "address": {"street": "Teststreet", "city": "New York"}}]))
                                                                                    
        propertyDef = PropertyDefinition("identifier", "category", property_type.ObjectType("datafinder_test.core.item.property_test.AddressPropertyMock"))
        propertyDef.defaultValue = "Test"
        self._property = Property.create(propertyDef, SimpleMock([{"street": "Teststreet", "city": "New York"}]))
        self.assertEquals(self._property.value, {"city": "New York", "street": "Teststreet"})
        self.assertEquals(self._property.additionalValueRepresentations, list())
    
    def testComparison(self):
        """ Tests the comparison of two instances. """
        
        self.assertEquals(self._property, self._property)
        self.assertEquals(self._property, Property(self._property.propertyDefinition, "value"))
        self.assertNotEquals(self._property, Property(SimpleMock(), "value"))


class StandardBaseModel(object):
    """ A simple example property model class. """
    
    def __init__(self):
        """
        Constructor.
        """
        
        pass
        
    def fromDict(self, value):
        """ 
        Loads the object from a given dict.
        
        @param value: A dict representing the object. 
        """
        
        for key in self.__dict__:
            if issubclass(self.__dict__[key].__class__, StandardBaseModel):
                self.__dict__[key] = self.__dict__[key].fromDict(value[key])
            else:
                self.__dict__[key] = value[key]
        return self
    
    def toDict(self):
        """ Returns the object as dict. """
        
        resultDict = dict()
        for key in self.__dict__:
            if issubclass(self.__dict__[key].__class__, StandardBaseModel):
                resultDict[key] = self.__dict__[key].toDict()
            else:
                resultDict[key] = self.__dict__[key]
        return resultDict
     
    def validate(self, value):
        """ 
        Calls all checks on the given value.
        
        @param value: A dict representing an object. 
        """
        
        if len(self.__dict__) == len(value):
            try:
                for key in self.__dict__:
                    if issubclass(self.__dict__[key].__class__, StandardBaseModel) and isinstance(value[key], type(dict())):
                        self.__dict__[key].validate(value[key])
                    elif type(self.__dict__[key]) == type(value[key]):
                        pass
                    else:
                        raise ValidationError("The given object does not match the defined object.")
            except KeyError:
                raise ValidationError("The given object does not match the defined object.")
            except TypeError:
                raise ValidationError("The given object does not match the defined object.")
        else:
            raise ValidationError("The given object does not match the defined object.")
        
    def helpText(self, propertyName):
        pass
    
    def displayName(self, propertyName):
        pass


class AuthorPropertyMock(StandardBaseModel):
    """ A simple property model class. """
    
    def __init__(self):
        """
        Constructor.
        """
        
        self.firstName = ""
        self.lastName = ""
        self.email = ""
        self.address = AddressPropertyMock()
        
        
class AddressPropertyMock(StandardBaseModel):
    """ A simple property model class. """
    
    def __init__(self):
        """
        Constructor.
        """
        
        self.street = ""
        self.city = ""
    