# pylint: disable=W0212
# W0212: It is fine for test purposes to access protected members.
#
# $Filename$ 
# $Authors$
#
# Last Changed: $Date$ $Committer$ $Revision-Id$
#
# Copyright (c) 2003-2011, German Aerospace Center (DLR)
# All rights reserved.
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
Test case for the property support module.
"""


import unittest

from datafinder.core.configuration.properties.registry import PropertyDefinitionRegistry
from datafinder.core.configuration.properties.property_definition import PropertyDefinitionFactory
from datafinder.core.error import ItemError, PropertyError
from datafinder.script_api.error import ItemSupportError, PropertySupportError
from datafinder.script_api.properties import property_support as prop_supp
from datafinder.script_api.properties import StringType
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class _PropertyMock(object):
    def __init__(self, identifier="", value=""):
        self.identifier = identifier
        self.value = value
        self.propertyDefinition = SimpleMock(category="user")


class _ItemMock(object):
    error = False
    def __init__(self, path="", properties=dict()):
        self.path = path    
        self.properties = properties
        
    def updateProperties(self, properties):
        self._raiseError()
        self.properties.clear()
        for prop in properties:
            self.properties[prop.identifier] = prop
        
    def deleteProperties(self, _):
        self._raiseError()
        
    def _raiseError(self):
        if self.error:
            raise ItemError("")

    
class _RepositoryMock(object):
    error = False
    propError = False
    def __init__(self, itemMock, propRegistry):
        self.itemMock = itemMock 
        self.propRegistry = propRegistry
    
    def createProperty(self, propId, value):
        if self.propError:
            raise PropertyError(propId, "")
        return _PropertyMock(propId, value)
    
    def getItem(self, _):
        if self.error:
            raise ItemError("")
        return self.itemMock
    
    @property
    def configuration(self):
        return SimpleMock(
            propertyDefinitionFactory=self.propRegistry._propertyDefinitionFactory,
            propertyDefinitionRegistry=self.propRegistry)

    
class PropertySupportTestCase(unittest.TestCase):
    
    def setUp(self):
        self._itemMock = _ItemMock()
        self._propRegistry = PropertyDefinitionRegistry(PropertyDefinitionFactory(), True)
        self._repositoryMock = _RepositoryMock(self._itemMock, self._propRegistry)
        self._repositoryManagerInstanceMock = \
            SimpleMock(workingRepository=self._repositoryMock)
        prop_supp.repositoryManagerInstance = self._repositoryManagerInstanceMock
        
    def testRetrieveProperties(self):
        # Success
        self._itemMock.properties = {"propertyId": _PropertyMock()}
        self.assertEquals(prop_supp.retrieveProperties("/item"), 
                          {"propertyId": ""})
        
        # Problems during retrieval
        self._repositoryMock.error = True
        self.assertRaises(ItemSupportError, prop_supp.retrieveProperties, "/item")

    def testStoreProperties(self):
        # Success
        self._itemMock.properties = {"name": _PropertyMock("name", "AnotherName")}
        properties = {"name": "TheName", "price": 120}
        prop_supp.storeProperties("/item", properties)
        self.assertEquals(prop_supp.retrieveProperties("/item"), properties)
        
        # Cannot set specific property
        self._repositoryMock.propError = True
        self.assertRaises(
            ItemSupportError, prop_supp.storeProperties, "/item", {"n2": None})
        
        # Cannot store them
        self._itemMock.error = True
        self.assertRaises(ItemSupportError, prop_supp.storeProperties, "/item", dict())
        
        # Cannot find item
        self._repositoryMock.error = True
        self.assertRaises(ItemSupportError, prop_supp.storeProperties, "/item", dict())

    def testDeleteProperties(self):
        # Success
        prop_supp.deleteProperties("/item", ["name", "price"])
        
        # Cannot delete system-specific properties
        self.assertRaises(
            ItemSupportError, prop_supp.deleteProperties, "/item", ["____size____"])
        
        # Cannot delete them
        self._itemMock.error = True
        self.assertRaises(ItemSupportError, prop_supp.deleteProperties, "/Item", list())

        # Cannot find item
        self._repositoryMock.error = True
        self.assertRaises(ItemSupportError, prop_supp.deleteProperties, "/Item", list())

    def testValidate(self):
        # Success
        prop_supp.validate({"name": "name", "price": 123})
        
        # Values does not fit
        self.assertRaises(PropertySupportError, prop_supp.validate, {"____size____": "name"})
        
    def testPropertyDescription(self):
        propDesc = prop_supp.propertyDescription("id")
        self.assertEquals(propDesc.identifier, "id")
        self.assertEquals(propDesc.type, "Any")
        self.assertEquals(propDesc.displayName, "id")
        self.assertEquals(propDesc.category, "____user____")
        self.assertEquals(propDesc.description, None)
        self.assertEquals(propDesc.defaultValue, None)
        self.assertEquals(propDesc.notNull, False)
        self.assertEquals(propDesc.namespace, None)
        self.assertEquals(len(propDesc.restrictions), 1)
        self.assertEquals(repr(propDesc), "id Type: Any Category: ____user____")

    def testAvailableProperties(self):
        self.assertEquals(len(prop_supp.availableProperties()), 
                          len(self._propRegistry.registeredPropertyDefinitions))
        
    def testRegisterPropertyDefinition(self):
        # Success
        prop_supp.registerPropertyDefinition("name", StringType(), "displayName", "helpText")
        propDesc = prop_supp.propertyDescription("name")
        self.assertEquals(propDesc.identifier, "name")
        self.assertEquals(propDesc.type, "String")
        self.assertEquals(propDesc.displayName, "displayName")
        self.assertEquals(propDesc.category, "____user____")
        self.assertEquals(propDesc.description, "helpText")
        self.assertEquals(propDesc.defaultValue, None)
        self.assertEquals(propDesc.notNull, False)
        self.assertEquals(propDesc.namespace, None)
        self.assertEquals(propDesc.restrictions, dict())
        self.assertEquals(repr(propDesc), "name Type: String Category: ____user____")
        
        # System-specific property exists
        self.assertRaises(PropertySupportError, prop_supp.registerPropertyDefinition, 
                          "____size____", StringType())
        
        # Property identifier does not match
        self._propRegistry._propertyDefinitionFactory.propertyIdValidator = lambda _: (False, 0)
        self.assertRaises(PropertySupportError, prop_supp.registerPropertyDefinition, 
                          "id", StringType())
        