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
Tests of the data type representation.
"""


import unittest

from datafinder.core.configuration.datamodel import datatype
from datafinder.core.configuration.properties.constants import DATAMODEL_PROPERTY_CATEGORY
from datafinder_test.mocks import SimpleMock


__version__ = "$Revision-Id:$" 


class DataTypeTestCase(unittest.TestCase):
    """ Tests of the data type representation. """

    def setUp(self):
        """ Creates object under test. """
        
        self._dataType = datatype.DataType("name")
        
    def testPropertyDefinitionHandling(self):
        """  Tests the handling of property definitions. """
        
        self._dataType.addPropertyDefinition(SimpleMock(identifier="name"))
        self._dataType.addPropertyDefinition(SimpleMock(identifier="name2"))
        self.assertEquals(len(self._dataType.propertyDefinitions), 2)
        
        self._dataType.addPropertyDefinition(SimpleMock(identifier="name"))
        self.assertEquals(len(self._dataType.propertyDefinitions), 2)
        
        self._dataType.removePropertyType("name")
        self._dataType.removePropertyType("name2")
        self.assertEquals(len(self._dataType.propertyDefinitions), 0)
        
        self._dataType.propertyDefinitions = [SimpleMock(identifier="name"), SimpleMock(identifier="name2")]
        self.assertEquals(len(self._dataType.propertyDefinitions), 2)
        
    def testComparison(self):
        """ Tests the comparison of two data type instances. """
        
        self.assertEquals(self._dataType, self._dataType)
        self.assertEquals(self._dataType, datatype.DataType("name"))
        self.assertNotEquals(self._dataType, datatype.DataType("name1"))
        self.assertNotEquals(self._dataType, None)
        
    def testLoad(self):
        """ Tests the initialization from persistence format. """
        
        persistedDataType = SimpleMock(name="name", iconName="iconName", 
                                       properties=[SimpleMock(name="name", valueType="Any", 
                                                              defaultValue="string", mandatory=False)]) 
        dataType = datatype.DataType.load(persistedDataType)
        self.assertEquals(dataType.name, "name")
        self.assertEquals(dataType.iconName, "iconName")
        self.assertEquals(len(dataType.propertyDefinitions), 1)
        self.assertEquals(dataType.propertyDefinitions[0].category, DATAMODEL_PROPERTY_CATEGORY)
        self.assertEquals(dataType.propertyDefinitions[0].namespace, self._dataType.name)

    def testToPersistenceRepresentation(self):
        """ Tests the transformation into the persistence format. """
        
        self._dataType.addPropertyDefinition(SimpleMock("name"))
        persistedDataType = self._dataType.toPersistenceRepresentation()
        self.assertEquals(persistedDataType.name, "name")
        self.assertEquals(persistedDataType.iconName, "dataType")
        self.assertEquals(len(persistedDataType.properties), 1)
