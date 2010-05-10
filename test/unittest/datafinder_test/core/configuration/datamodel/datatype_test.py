#
# Created: 12.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: datatype_test.py 4100 2009-05-24 18:12:19Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests of the data type representation.
"""


import unittest

from datafinder.core.configuration.datamodel import datatype
from datafinder.core.configuration.properties.constants import DATAMODEL_PROPERTY_CATEGORY
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4100 $"


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
