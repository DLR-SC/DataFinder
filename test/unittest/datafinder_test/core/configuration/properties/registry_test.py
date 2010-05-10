#
# Created: 30.05.2008 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: registry_test.py 3994 2009-05-05 08:22:19Z schlauch $ 
# 
# Copyright (C) 2003-2008 DLR/SISTEC, Germany
# 
# All rights reserved
# 
# http://www.dlr.de/datafinder/
#


""" 
Test module for the property type registry.
"""


import unittest

from datafinder.core.configuration.properties import constants
from datafinder.core.configuration.properties.property_definition import PropertyDefinition
from datafinder.core.configuration.properties.registry import PropertyDefinitionRegistry
from datafinder.core.configuration.properties import property_type
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 3994 $"


class PropertyTypeRegistryTestCase(unittest.TestCase):
    """ Tests for the module property_type_registry. """
    
    def setUp(self):
        """ Creates the required test environment. """
        
        self.__propertyDef = PropertyDefinition("testID", constants.USER_PROPERTY_CATEGORY, property_type.StringType())
        self.__registry = PropertyDefinitionRegistry(SimpleMock(), False)
        self.__lenRegisteredProperties = len(self.__registry.registeredPropertyDefinitions)
    
    def tearDown(self):
        """ Cleans up test environment. """
        
        self.__registry.unregister([self.__propertyDef])
    
    def testRemovingOfNonExistingPropertyType(self):
        """ Tests the removing of a non-existing property type definition. """
        
        self.__registry.unregister([self.__propertyDef])
        self.assertEquals(len(self.__registry.registeredPropertyDefinitions), self.__lenRegisteredProperties)
        
    def testMuliplePropertyTypeAdding(self):
        """ Tests the multiple adding of the identical property type definition. """
        
        self.__registry.register([self.__propertyDef, self.__propertyDef])
        self.assertEquals(len(self.__registry.registeredPropertyDefinitions), self.__lenRegisteredProperties + 1)
        
    def testRegisterPropertyType(self):
        """ Tests the registering of a property type. """
        
        self.__registry.register([self.__propertyDef])
        self.failIf((self.__propertyDef.namespace, self.__propertyDef.identifier) not in self.__registry.registeredPropertyDefinitions, 
                    "The property was not registered.")
        self.__registry.unregister([self.__propertyDef])
        self.failIf((self.__propertyDef.namespace, self.__propertyDef.identifier) in self.__registry.registeredPropertyDefinitions, 
                    "The property was not unregistered.")

    def testUnregisterPropertyType(self):
        """ Tests the registering of a property type. """
        
        self.__registry.unregister([self.__propertyDef])
        self.failIf(self.__propertyDef.identifier in self.__registry.registeredPropertyDefinitions, "The property was not unregistered.")

    def testPropertyTypeMappingUnmodifiable(self):
        """ Tests that property type mapping cannot be changed from outside. """
        
        registeredProperties = self.__registry.registeredPropertyDefinitions
        for propertyDef in registeredProperties:
            if not propertyDef in self.__registry.registeredPropertyDefinitions:
                self.fail("Property definition not available.")
        registeredProperties[self.__propertyDef.identifier] = self.__propertyDef
        self.assertEquals(len(self.__registry.registeredPropertyDefinitions), self.__lenRegisteredProperties)
        
        equal = True
        for propertyDef in registeredProperties:
            if not propertyDef in self.__registry.registeredPropertyDefinitions:
                equal = False
        if equal:
            self.fail("Property definition changed from outside.")
        
    def testUpdateRegisteredPropertyType(self):
        """ Tests the update of a registered property type definition. """
        
        self.__registry.register([self.__propertyDef])
        self.__propertyDef.description = "New Description"
        self.__registry.register([self.__propertyDef])
        
        propertyDefRegistry = self.__registry.registeredPropertyDefinitions[(self.__propertyDef.namespace, self.__propertyDef.identifier)]
        self.assertEquals(propertyDefRegistry.description, self.__propertyDef.description)
