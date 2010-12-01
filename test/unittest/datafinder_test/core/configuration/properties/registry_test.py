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
from datafinder.core.configuration.properties.property_definition import PropertyDefinition
from datafinder.core.configuration.properties.registry import PropertyDefinitionRegistry
from datafinder.core.configuration.properties import property_type
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


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
