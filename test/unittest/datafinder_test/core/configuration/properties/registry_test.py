# pylint: disable=W0212
# W0212: It is fine to access protected members for test purposes.
#
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


""" 
Test module for the property type registry.
"""


import unittest

from datafinder.core.configuration.properties import constants
from datafinder.core.configuration.properties.property_definition import PropertyDefinition, PropertyDefinitionFactory
from datafinder.core.configuration.properties.registry import PropertyDefinitionRegistry
from datafinder.core.configuration.properties import property_type
from datafinder.core.error import ConfigurationError


__version__ = "$Revision-Id:$" 


class PropertyTypeRegistryTestCase(unittest.TestCase):
    """ Tests for the module property_type_registry. """
    
    def setUp(self):
        """ Creates the required test environment. """
        
        self._propDef = PropertyDefinition(
            "testID", constants.USER_PROPERTY_CATEGORY, property_type.StringType())
        self._registry = PropertyDefinitionRegistry(PropertyDefinitionFactory(), True)
        self._regPropsNumber = len(self._registry.registeredPropertyDefinitions)
    
    def tearDown(self):
        """ Cleans up test environment. """
        
        self._registry.unregister([self._propDef])
    
    def testRemovingOfNonExistingPropertyType(self):
        """ Tests the removing of a non-existing property type definition. """
        
        self._registry.unregister([self._propDef])
        self.assertEquals(len(self._registry.registeredPropertyDefinitions), 
            self._regPropsNumber)
        
    def testMuliplePropertyTypeAdding(self):
        """ Tests the multiple adding of the identical property type definition. """
        
        self._registry.register([self._propDef, self._propDef])
        self.assertEquals(
            len(self._registry.registeredPropertyDefinitions), self._regPropsNumber + 1)
        
    def testRegisterPropertyType(self):
        """ Tests the registering of a property type. """
        
        self._registry.register([self._propDef])
        self.failIf(
            not self._registry.isPropertyDefinitionRegistered(self._propDef), 
            "The property was not registered.")
        
        # Trying to register a system-specific properties again
        systemPropDef = self._registry.systemPropertyDefinitions[0]
        self.assertTrue(self._registry.existsSystemPropertyDefinition(systemPropDef.identifier))
        self.assertRaises(ConfigurationError, self._registry.register, [systemPropDef])
        
        self._registry.clear()
        self.assertEquals(len(self._registry.registeredPropertyDefinitions), 
                          self._regPropsNumber)
        self.assertEquals(len(self._registry.systemPropertyDefinitions), 
                          self._regPropsNumber)

    def testUnregisterPropertyType(self):
        """ Tests the registering of a property type. """
        
        self._registry.register([self._propDef])
        self._registry.unregister([self._propDef])
        self.failIf(
            self._registry.isPropertyDefinitionRegistered(self._propDef), 
            "The property was not registered.")

    def testPropertyTypeMappingUnmodifiable(self):
        """ Tests that property type mapping cannot be changed from outside. """
        
        registeredProperties = self._registry.registeredPropertyDefinitions
        for propertyDef in registeredProperties:
            if not propertyDef in self._registry.registeredPropertyDefinitions:
                self.fail("Property definition not available.")
        registeredProperties[self._propDef.identifier] = self._propDef
        self.assertEquals(
            len(self._registry.registeredPropertyDefinitions), self._regPropsNumber)
        
        equal = True
        for propertyDef in registeredProperties:
            if not propertyDef in self._registry.registeredPropertyDefinitions:
                equal = False
        if equal:
            self.fail("Property definition changed from outside.")
        
    def testUpdateRegisteredPropertyType(self):
        """ Tests the update of a registered property type definition. """
        
        self._registry.register([self._propDef])
        self._propDef.description = "New Description"
        self._registry.register([self._propDef])
        
        propertyDefRegistry = self._registry.registeredPropertyDefinitions\
            [(self._propDef.namespace, self._propDef.identifier)]
        self.assertEquals(propertyDefRegistry.description, self._propDef.description)

    def testGetPropertyDefinition(self):
        self._registry.register([self._propDef])
        retrievedPropDef = self._registry.getPropertyDefinition(self._propDef.identifier)
        self.assertEquals(retrievedPropDef, self._propDef)
        self.assertNotEquals(id(retrievedPropDef), id(self._propDef))
        
        # Non-registered properties are created
        newPropDef = self._registry.getPropertyDefinition("new")
        self.assertTrue(not self._registry.isPropertyDefinitionRegistered(newPropDef)) # but not registered

    def testDataFields(self):
        """ Checks the different attributes data / fields. """
        
        self.assertEquals(self._registry.defaultArchivePropertyDefinitions,
                          self._registry._defaultArchivePropertyDefinitions)
        self.assertNotEquals(id(self._registry.defaultArchivePropertyDefinitions),
                             id(self._registry._defaultArchivePropertyDefinitions))
        
        self.assertEquals(self._registry.defaultResourcePropertyDefinitions,
                          self._registry._defaultResourcePropertyDefinitions)
        self.assertNotEquals(id(self._registry.defaultResourcePropertyDefinitions),
                             id(self._registry._defaultResourcePropertyDefinitions))
        
        self.assertEquals(self._registry.defaultCollectionPropertyDefinitions,
                          self._registry._defaultCollectionPropertyDefinitions)
        self.assertNotEquals(id(self._registry.defaultCollectionPropertyDefinitions),
                             id(self._registry._defaultCollectionPropertyDefinitions))
        
        self.assertEquals(self._registry.registeredPropertyDefinitions,
                          self._registry._registeredPropertyDefinitions)
        self.assertNotEquals(id(self._registry.registeredPropertyDefinitions),
                             id(self._registry._registeredPropertyDefinitions))
        
        self.assertEquals(self._registry.systemPropertyDefinitions,
                          self._registry._systemPropertyDefinitions)
        self.assertNotEquals(id(self._registry.systemPropertyDefinitions),
                             id(self._registry._systemPropertyDefinitions))

    def testPropertyNameValidationFunction(self):
        """ Ensures that the extended check function works as expected. """
        
        # Check for non-existing ID
        testFunction = self._registry.propertyNameValidationFunction
        self.assertEquals(testFunction("unknownId"), True)
        
        # Check for existing ID
        self._registry.register([self._propDef])
        testFunction = self._registry.propertyNameValidationFunction
        self.assertEquals(testFunction(self._propDef.identifier), False)
