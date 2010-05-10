#
# Created: 12.04.2009 schlauch <Tobias.Schlauch@dlr.de>
# Changed: $Id: relation_test.py 4100 2009-05-24 18:12:19Z schlauch $ 
# 
# Copyright (c) 2008, German Aerospace Center (DLR)
# All rights reserved.
# 
# http://www.dlr.de/datafinder/
#


""" 
Tests the relation representation.
"""


import unittest

from datafinder.core.configuration.datamodel import relation
from datafinder_test.mocks import SimpleMock


__version__ = "$LastChangedRevision: 4100 $"


class RelationTestCase(unittest.TestCase):
    """ Tests the relation representation. """

    def setUp(self):
        """ Creates object under test. """
        
        self._relation = relation.Relation("name")
    
    def testSourceDataTypeHandling(self):
        """ Tests the handling of source data type names. """
        
        self._relation.addSourceDataTypeName("name")
        self._relation.addSourceDataTypeName("name2")
        self.assertEquals(len(self._relation.sourceDataTypeNames), 2)
        
        self._relation.addSourceDataTypeName("name2")
        self.assertEquals(len(self._relation.sourceDataTypeNames), 2)
        
        self._relation.removeSourceDataTypeName("name")
        self._relation.removeSourceDataTypeName("name2")
        self.assertEquals(len(self._relation.sourceDataTypeNames), 0)
        
        self._relation.sourceDataTypeNames = ["name", "name2"] 
        self.assertEquals(len(self._relation.sourceDataTypeNames), 2)
        
    def testTargetDataTypeHandling(self):
        """ Tests the handling of target data type names. """
        
        self._relation.addTargetDataTypeName("name")
        self._relation.addTargetDataTypeName("name2")
        self.assertEquals(len(self._relation.targetDataTypeNames), 2)
        
        self._relation.addTargetDataTypeName("name2")
        self.assertEquals(len(self._relation.targetDataTypeNames), 2)
        
        self._relation.removeTargetDataTypeName("name")
        self._relation.removeTargetDataTypeName("name2")
        self.assertEquals(len(self._relation.targetDataTypeNames), 0)
        
    def testLoad(self):
        """ Tests the creation of a relation from the persistence format. """
        
        newRelation = relation.Relation.load(SimpleMock(name="name", iconName="iconName",
                                                        sourceDataTypeNames=["a", "b"],
                                                        targetDataTypeNames=["c", "d"]))
        self.assertEquals(newRelation.name, "name")
        self.assertEquals(newRelation.iconName, "iconName")
        self.assertEquals(newRelation.sourceDataTypeNames, ["a", "b"])
        self.assertEquals(newRelation.targetDataTypeNames, ["c", "d"])
        
    def testToPersistenceRepresentation(self):
        """ Tests the transformation to the persistence format. """
        
        self._relation.sourceDataTypeNames = ["a"]
        self._relation.targetDataTypeNames = ["a"]
        
        persistedDataType = self._relation.toPersistenceRepresentation()
        self.assertEquals(persistedDataType.name, "name")
        self.assertEquals(persistedDataType.iconName, "relationType")
        self.assertEquals(persistedDataType.sourceDataTypeNames, ["a"])
        self.assertEquals(persistedDataType.targetDataTypeNames, ["a"])
